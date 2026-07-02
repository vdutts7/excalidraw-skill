#!/usr/bin/env python3
"""
excalidraw/scripts/generate.py
Canonical .excalidraw v2 JSON generator.
Usage:
  python3 generate.py <plan.json>          # generate from element plan
  python3 generate.py --validate <file>   # validate existing .excalidraw file
  python3 generate.py --skeleton          # print empty document skeleton

Element plan format:
  { "output": "filename.excalidraw", "elements": [ <element_defs> ] }

Element def shortcuts (generate.py auto-fills required base fields):
  { "kind": "rect",    "id", "x","y","w","h", "bg","stroke", "label"?, "fontSize"?, "roughness"? }
  { "kind": "zone",    "id", "x","y","w","h", "bg","stroke" }
  { "kind": "text",    "id", "x","y","w","h", "text", "fontSize"?, "color"?, "align"? }
  { "kind": "arrow",   "id", "x","y", "dx","dy", "stroke"?, "strokeStyle"?, "label"?, "startHead"?, "endHead"? }
  { "kind": "diamond", "id", "x","y","w","h", "bg","stroke", "label"? }
  { "kind": "ellipse", "id", "x","y","w","h", "bg","stroke", "label"? }
  { "kind": "raw",     ... full excalidraw element ... }
"""

import json
import sys
import random
import time
import argparse
from pathlib import Path

# ── Constants from excalidraw/packages/common/src/constants.ts ──────────────

ROUGHNESS = {"architect": 0, "artist": 1, "cartoonist": 2}
STROKE_WIDTH = {"thin": 1, "bold": 2, "extraBold": 4}
FONT_FAMILY = {
    "Virgil": 1, "Helvetica": 2, "Cascadia": 3,
    "Excalifont": 5, "Nunito": 6, "Lilita One": 7,
    "Comic Shanns": 8, "Liberation Sans": 9,
}
ROUNDNESS = {"LEGACY": 1, "PROPORTIONAL_RADIUS": 2, "ADAPTIVE_RADIUS": 3}

# Default props from DEFAULT_ELEMENT_PROPS in constants.ts
DEFAULTS = {
    "strokeColor": "#1e1e1e",
    "backgroundColor": "transparent",
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 1,          # ROUGHNESS.artist
    "opacity": 100,
    "locked": False,
    "angle": 0,
    "groupIds": [],
    "frameId": None,
    "isDeleted": False,
    "link": None,
    "boundElements": None,
    "version": 1,
    "lineHeight": 1.25,
    "fontSize": 16,
    "fontFamily": 1,         # Virgil
    "textAlign": "center",
    "verticalAlign": "middle",
}

# Semantic arch palette (from excalidraw-toolkit colors.md + COLOR_PALETTE)
ARCH_COLORS = {
    "frontend":  {"bg": "#a5d8ff", "stroke": "#1971c2"},
    "backend":   {"bg": "#d0bfff", "stroke": "#7048e8"},
    "database":  {"bg": "#b2f2bb", "stroke": "#2f9e44"},
    "cache":     {"bg": "#ffe8cc", "stroke": "#fd7e14"},
    "queue":     {"bg": "#fff3bf", "stroke": "#fab005"},
    "storage":   {"bg": "#ffec99", "stroke": "#f08c00"},
    "ai":        {"bg": "#e599f7", "stroke": "#9c36b5"},
    "external":  {"bg": "#ffc9c9", "stroke": "#e03131"},
    "decision":  {"bg": "#ffd8a8", "stroke": "#e8590c"},
    "zone":      {"bg": "#e9ecef", "stroke": "#868e96"},
    "primary_node":    {"bg": "#d3f9d8", "stroke": "#2f9e44"},
    "restricted_node": {"bg": "#ffe3e3", "stroke": "#c92a2a"},
    "client_node":     {"bg": "#e3f2fd", "stroke": "#1864ab"},
    "secure_store":    {"bg": "#e5dbff", "stroke": "#7048e8"},
    "buffer_zone":     {"bg": "#fff3bf", "stroke": "#e67700"},
    "neutral":   {"bg": "#f8f9fa", "stroke": "#495057"},
}


# ── Helpers ──────────────────────────────────────────────────────────────────

_idx_counter = 0
_idx_prefixes = ["a", "b", "c", "d", "e", "f", "g", "h"]

def _next_index(prefix="a"):
    global _idx_counter
    _idx_counter += 1
    n = _idx_counter
    # simple base-26 fractional index style
    return f"{prefix}{n:03d}"

def _seed():
    return random.randint(100000, 9999999)

def _updated():
    return int(time.time() * 1000)

def _uid(hint=""):
    return f"{hint}{random.randint(10000,99999)}"


# ── Base element builder ──────────────────────────────────────────────────────

def base(type_, id_, x, y, w, h, index, **kwargs):
    """Build a complete base element dict with all required fields."""
    el = {
        "id": id_,
        "type": type_,
        "x": x, "y": y,
        "width": w, "height": h,
        "angle": kwargs.pop("angle", 0),
        "strokeColor": kwargs.pop("stroke", kwargs.pop("strokeColor", DEFAULTS["strokeColor"])),
        "backgroundColor": kwargs.pop("bg", kwargs.pop("backgroundColor", DEFAULTS["backgroundColor"])),
        "fillStyle": kwargs.pop("fillStyle", DEFAULTS["fillStyle"]),
        "strokeWidth": kwargs.pop("strokeWidth", DEFAULTS["strokeWidth"]),
        "strokeStyle": kwargs.pop("strokeStyle", DEFAULTS["strokeStyle"]),
        "roughness": kwargs.pop("roughness", DEFAULTS["roughness"]),
        "opacity": kwargs.pop("opacity", DEFAULTS["opacity"]),
        "groupIds": kwargs.pop("groupIds", []),
        "frameId": kwargs.pop("frameId", None),
        "index": index,
        "roundness": kwargs.pop("roundness", None),
        "seed": kwargs.pop("seed", _seed()),
        "version": kwargs.pop("version", 1),
        "versionNonce": kwargs.pop("versionNonce", _seed()),
        "isDeleted": False,
        "boundElements": kwargs.pop("boundElements", None),
        "updated": kwargs.pop("updated", _updated()),
        "link": None,
        "locked": False,
    }
    return el


# ── Shape builders ────────────────────────────────────────────────────────────

def make_rect(id_, x, y, w, h, bg="transparent", stroke="#1e1e1e",
              roughness=1, strokeWidth=2, strokeStyle="solid",
              opacity=100, rounded=True, index=None):
    """Rectangle with ADAPTIVE_RADIUS roundness."""
    el = base("rectangle", id_, x, y, w, h,
              index=index or _next_index("a"),
              bg=bg, stroke=stroke,
              roughness=roughness, strokeWidth=strokeWidth,
              strokeStyle=strokeStyle, opacity=opacity,
              roundness={"type": ROUNDNESS["ADAPTIVE_RADIUS"]} if rounded else None)
    return el


def make_zone(id_, x, y, w, h, bg="#e9ecef", stroke="#868e96", index=None):
    """Background zone rectangle — low opacity, dashed, roughness=0."""
    el = base("rectangle", id_, x, y, w, h,
              index=index or _next_index("Z"),
              bg=bg, stroke=stroke,
              roughness=0, strokeWidth=1, strokeStyle="dashed",
              opacity=40,
              roundness={"type": ROUNDNESS["ADAPTIVE_RADIUS"]})
    return el


def make_diamond(id_, x, y, w, h, bg="transparent", stroke="#1e1e1e",
                 roughness=1, index=None):
    el = base("diamond", id_, x, y, w, h,
              index=index or _next_index("a"),
              bg=bg, stroke=stroke, roughness=roughness,
              roundness={"type": ROUNDNESS["PROPORTIONAL_RADIUS"]})
    return el


def make_ellipse(id_, x, y, w, h, bg="transparent", stroke="#1e1e1e",
                 roughness=1, index=None):
    el = base("ellipse", id_, x, y, w, h,
              index=index or _next_index("a"),
              bg=bg, stroke=stroke, roughness=roughness,
              roundness={"type": ROUNDNESS["PROPORTIONAL_RADIUS"]})
    return el


def make_text(id_, x, y, w, h, text, fontSize=16, fontFamily=1,
              color="#1e1e1e", align="center", valign="middle",
              containerId=None, index=None):
    """Standalone or contained text element."""
    el = base("text", id_, x, y, w, h,
              index=index or _next_index("c"),
              bg="transparent", stroke=color,
              roughness=1, strokeWidth=1,
              roundness=None, boundElements=[])
    el.update({
        "text": text,
        "originalText": text,
        "fontSize": fontSize,
        "fontFamily": fontFamily,
        "textAlign": align,
        "verticalAlign": valign,
        "containerId": containerId,
        "autoResize": True,
        "lineHeight": 1.25,
    })
    return el


def make_arrow(id_, x, y, dx, dy,
               stroke="#1e1e1e", strokeStyle="solid", strokeWidth=2,
               roughness=1, startHead=None, endHead="arrow",
               startBinding=None, endBinding=None,
               elbowed=False, index=None):
    """
    Arrow from (x,y) to (x+dx, y+dy).
    points[0] always [0,0]; points[1] is [dx,dy].
    width/height = abs(dx), abs(dy).
    """
    el = base("arrow", id_, x, y, abs(dx), abs(dy),
              index=index or _next_index("b"),
              bg="transparent", stroke=stroke,
              roughness=roughness, strokeWidth=strokeWidth,
              strokeStyle=strokeStyle,
              roundness={"type": ROUNDNESS["PROPORTIONAL_RADIUS"]},
              boundElements=[])
    el.update({
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": startBinding,
        "endBinding": endBinding,
        "startArrowhead": startHead,
        "endArrowhead": endHead,
        "elbowed": elbowed,
    })
    return el


def make_arrow_elbow(id_, x, y, dx, dy,
                     stroke="#1e1e1e", strokeStyle="solid", strokeWidth=2,
                     roughness=1, startHead=None, endHead="arrow", index=None):
    """L-shaped elbow arrow: goes down dy/2, then right dx (or vice versa)."""
    mid_y = dy // 2
    points = [[0, 0], [0, mid_y], [dx, mid_y], [dx, dy]]
    el = base("arrow", id_, x, y, abs(dx), abs(dy),
              index=index or _next_index("b"),
              bg="transparent", stroke=stroke,
              roughness=roughness, strokeWidth=strokeWidth,
              strokeStyle=strokeStyle,
              roundness={"type": ROUNDNESS["PROPORTIONAL_RADIUS"]},
              boundElements=[])
    el.update({
        "points": points,
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": startHead,
        "endArrowhead": endHead,
        "elbowed": True,
    })
    return el


def make_label_for_shape(shape_el, text, fontSize=16, fontFamily=1, color="#1e1e1e"):
    """
    Create a text element bound inside a shape, and mutate the shape's boundElements.
    Returns the text element. Modifies shape_el in place.
    """
    label_id = shape_el["id"] + "-lbl"
    txt = make_text(
        label_id,
        shape_el["x"], shape_el["y"],
        shape_el["width"], shape_el["height"],
        text, fontSize=fontSize, fontFamily=fontFamily,
        color=color, align="center", valign="middle",
        containerId=shape_el["id"],
        index=_next_index("c"),
    )
    # Mutate shape to track bound text
    if shape_el.get("boundElements") is None:
        shape_el["boundElements"] = []
    shape_el["boundElements"].append({"id": label_id, "type": "text"})
    return txt


# ── Document builder ──────────────────────────────────────────────────────────

def build_document(elements, source="excalidraw-skill", bg="#ffffff"):
    """Wrap elements in the canonical .excalidraw v2 root structure."""
    return {
        "type": "excalidraw",
        "version": 2,
        "source": source,
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": bg,
        },
        "files": {},
    }


# ── Plan executor ─────────────────────────────────────────────────────────────

def execute_plan(plan: dict) -> dict:
    """
    Build elements from a plan dict.
    plan = { "output": "file.excalidraw", "source": "...", "elements": [...] }

    Each element in plan["elements"] can be a 'kind' shorthand or a 'raw' full element.
    """
    raw_elements = []
    extra_labels = []  # text labels added by make_label_for_shape

    for el_def in plan.get("elements", []):
        kind = el_def.get("kind", "raw")

        if kind == "raw":
            raw_elements.append(el_def)

        elif kind == "zone":
            el = make_zone(
                el_def["id"],
                el_def["x"], el_def["y"],
                el_def.get("w", el_def.get("width", 400)),
                el_def.get("h", el_def.get("height", 200)),
                bg=el_def.get("bg", "#e9ecef"),
                stroke=el_def.get("stroke", "#868e96"),
                index=el_def.get("index"),
            )
            raw_elements.append(el)
            if el_def.get("label"):
                lbl = make_text(
                    el_def["id"] + "-title",
                    el_def["x"] + 12, el_def["y"] + 10,
                    200, 24,
                    el_def["label"],
                    fontSize=14, color=el_def.get("stroke", "#868e96"),
                    align="left",
                    index=_next_index("c"),
                )
                extra_labels.append(lbl)

        elif kind in ("rect", "rectangle"):
            el = make_rect(
                el_def["id"],
                el_def["x"], el_def["y"],
                el_def.get("w", el_def.get("width", 220)),
                el_def.get("h", el_def.get("height", 120)),
                bg=el_def.get("bg", "transparent"),
                stroke=el_def.get("stroke", "#1e1e1e"),
                roughness=el_def.get("roughness", 1),
                strokeWidth=el_def.get("strokeWidth", 2),
                strokeStyle=el_def.get("strokeStyle", "solid"),
                opacity=el_def.get("opacity", 100),
                rounded=el_def.get("rounded", True),
                index=el_def.get("index"),
            )
            raw_elements.append(el)
            if el_def.get("label"):
                lbl = make_label_for_shape(
                    el,
                    el_def["label"],
                    fontSize=el_def.get("fontSize", 16),
                    fontFamily=el_def.get("fontFamily", 1),
                    color=el_def.get("labelColor", "#1e1e1e"),
                )
                extra_labels.append(lbl)

        elif kind == "diamond":
            el = make_diamond(
                el_def["id"],
                el_def["x"], el_def["y"],
                el_def.get("w", 200), el_def.get("h", 120),
                bg=el_def.get("bg", "transparent"),
                stroke=el_def.get("stroke", "#1e1e1e"),
                roughness=el_def.get("roughness", 1),
                index=el_def.get("index"),
            )
            raw_elements.append(el)
            if el_def.get("label"):
                extra_labels.append(make_label_for_shape(el, el_def["label"],
                    fontSize=el_def.get("fontSize", 16)))

        elif kind == "ellipse":
            el = make_ellipse(
                el_def["id"],
                el_def["x"], el_def["y"],
                el_def.get("w", 200), el_def.get("h", 120),
                bg=el_def.get("bg", "transparent"),
                stroke=el_def.get("stroke", "#1e1e1e"),
                roughness=el_def.get("roughness", 1),
                index=el_def.get("index"),
            )
            raw_elements.append(el)
            if el_def.get("label"):
                extra_labels.append(make_label_for_shape(el, el_def["label"],
                    fontSize=el_def.get("fontSize", 16)))

        elif kind == "text":
            el = make_text(
                el_def["id"],
                el_def["x"], el_def["y"],
                el_def.get("w", 200), el_def.get("h", 25),
                el_def["text"],
                fontSize=el_def.get("fontSize", 16),
                fontFamily=el_def.get("fontFamily", 1),
                color=el_def.get("color", "#1e1e1e"),
                align=el_def.get("align", "center"),
                valign=el_def.get("valign", "middle"),
                containerId=el_def.get("containerId"),
                index=el_def.get("index"),
            )
            raw_elements.append(el)

        elif kind == "arrow":
            elbow = el_def.get("elbow", False)
            if elbow:
                el = make_arrow_elbow(
                    el_def["id"],
                    el_def["x"], el_def["y"],
                    el_def.get("dx", 0), el_def.get("dy", 0),
                    stroke=el_def.get("stroke", "#1e1e1e"),
                    strokeStyle=el_def.get("strokeStyle", "solid"),
                    strokeWidth=el_def.get("strokeWidth", 2),
                    roughness=el_def.get("roughness", 1),
                    startHead=el_def.get("startHead"),
                    endHead=el_def.get("endHead", "arrow"),
                    index=el_def.get("index"),
                )
            else:
                el = make_arrow(
                    el_def["id"],
                    el_def["x"], el_def["y"],
                    el_def.get("dx", 0), el_def.get("dy", 0),
                    stroke=el_def.get("stroke", "#1e1e1e"),
                    strokeStyle=el_def.get("strokeStyle", "solid"),
                    strokeWidth=el_def.get("strokeWidth", 2),
                    roughness=el_def.get("roughness", 1),
                    startHead=el_def.get("startHead"),
                    endHead=el_def.get("endHead", "arrow"),
                    index=el_def.get("index"),
                )
            raw_elements.append(el)
            # Arrow label as standalone floating text near midpoint
            if el_def.get("label"):
                mx = el_def["x"] + el_def.get("dx", 0) // 2 - 50
                my = el_def["y"] + el_def.get("dy", 0) // 2 - 15
                lbl = make_text(
                    el_def["id"] + "-lbl",
                    mx, my, 120, 22,
                    el_def["label"],
                    fontSize=el_def.get("fontSize", 13),
                    color=el_def.get("stroke", "#1e1e1e"),
                    align="center",
                    index=_next_index("c"),
                )
                extra_labels.append(lbl)

        else:
            print(f"[WARN] Unknown kind '{kind}', treating as raw", file=sys.stderr)
            raw_elements.append(el_def)

    all_elements = raw_elements + extra_labels
    return build_document(
        all_elements,
        source=plan.get("source", "excalidraw-skill"),
        bg=plan.get("bg", "#ffffff"),
    )


# ── Validator ─────────────────────────────────────────────────────────────────

REQUIRED_BASE = ["id","type","x","y","width","height","angle","strokeColor",
                  "backgroundColor","fillStyle","strokeWidth","strokeStyle",
                  "roughness","opacity","groupIds","frameId","index",
                  "roundness","seed","version","versionNonce","isDeleted",
                  "boundElements","updated","link","locked"]
REQUIRED_TEXT = ["text","originalText","fontSize","fontFamily","textAlign",
                  "verticalAlign","containerId","autoResize","lineHeight"]
REQUIRED_ARROW = ["points","startBinding","endBinding","startArrowhead","endArrowhead"]

def validate(doc: dict) -> list[str]:
    errors = []
    if doc.get("type") != "excalidraw":
        errors.append("ROOT: type must be 'excalidraw'")
    if doc.get("version") != 2:
        errors.append("ROOT: version must be 2")
    if "appState" not in doc:
        errors.append("ROOT: missing appState")
    if "files" not in doc:
        errors.append("ROOT: missing files")

    seen_ids = set()
    seen_indices = set()

    for i, el in enumerate(doc.get("elements", [])):
        tag = f"[{i}:{el.get('id','?')}]"

        if el.get("isDeleted"):
            continue  # skip deleted elements

        # Check id uniqueness
        eid = el.get("id")
        if eid in seen_ids:
            errors.append(f"{tag} duplicate id")
        seen_ids.add(eid)

        # Check index uniqueness
        idx = el.get("index")
        if idx and idx in seen_indices:
            errors.append(f"{tag} duplicate index '{idx}'")
        seen_indices.add(idx)

        # Check required base fields
        for f in REQUIRED_BASE:
            if f not in el:
                errors.append(f"{tag} missing required field '{f}'")

        # Type-specific checks
        t = el.get("type")
        if t == "text":
            for f in REQUIRED_TEXT:
                if f not in el:
                    errors.append(f"{tag} text missing '{f}'")
        elif t in ("arrow", "line"):
            for f in REQUIRED_ARROW:
                if f not in el:
                    errors.append(f"{tag} arrow missing '{f}'")
            pts = el.get("points", [])
            if not pts or pts[0] != [0, 0]:
                errors.append(f"{tag} arrow points[0] must be [0,0]")

        # Roundness type check
        r = el.get("roundness")
        if r and r.get("type") not in (1, 2, 3, None):
            errors.append(f"{tag} roundness type must be 1,2, or 3")

        # Arrow width/height check
        if t == "arrow":
            pts = el.get("points", [[0,0],[0,0]])
            expected_w = abs(pts[-1][0]) if len(pts) > 1 else 0
            expected_h = abs(pts[-1][1]) if len(pts) > 1 else 0
            if abs(el.get("width",0) - expected_w) > 2:
                errors.append(f"{tag} arrow width {el.get('width')} != abs(last dx) {expected_w}")

    return errors


# ── CLI ───────────────────────────────────────────────────────────────────────

def skeleton():
    doc = build_document([], source="excalidraw-skill")
    print(json.dumps(doc, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Excalidraw v2 JSON generator")
    parser.add_argument("input", nargs="?", help="Plan JSON file or .excalidraw to validate")
    parser.add_argument("--validate", metavar="FILE", help="Validate an existing .excalidraw file")
    parser.add_argument("--skeleton", action="store_true", help="Print empty document skeleton")
    parser.add_argument("--out", help="Output path (default: plan['output'] or stdout)")
    args = parser.parse_args()

    if args.skeleton:
        skeleton()
        return

    if args.validate:
        with open(args.validate) as f:
            doc = json.load(f)
        errors = validate(doc)
        if errors:
            print(f"INVALID — {len(errors)} error(s):")
            for e in errors:
                print(f"  ✗ {e}")
            sys.exit(1)
        else:
            el_count = len([e for e in doc["elements"] if not e.get("isDeleted")])
            print(f"VALID ✓ — {el_count} elements")
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    with open(args.input) as f:
        plan = json.load(f)

    doc = execute_plan(plan)

    # Validate before writing
    errors = validate(doc)
    if errors:
        print(f"[WARN] {len(errors)} validation issue(s):", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)

    out_path = args.out or plan.get("output", "output.excalidraw")
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"Written: {out_path} ({len(doc['elements'])} elements)")

    # Re-validate written file
    errors2 = validate(doc)
    if not errors2:
        print("Validation: PASS ✓")
    else:
        print(f"Validation: {len(errors2)} issue(s) remain", file=sys.stderr)

if __name__ == "__main__":
    main()
