---
name: excalidraw
description: >
  Generate valid .excalidraw files from any input — images, ASCII art, descriptions, existing
  diagrams, or convert /diagram output; Triggers: /excalidraw, "convert to excalidraw",
  "make excalidraw", "excalidraw style", "excalidraw file", "excalidraw diagram", or when user
  pastes/uploads an architecture diagram and wants a .excalidraw file back; Works WITHOUT MCP —
  pure Python JSON generation via scripts/generate.py → present_files; NOT for: /diagram
  (inline SVG), mermaid-only output, PNG-only output.
---

# /excalidraw

Branch of diagram (`registry/branches/excalidraw`). **Opt-in only** — enter when user explicitly requests excalidraw; never from default `/diagram` flow.

Generate canonical `.excalidraw` v2 JSON files from any input. No MCP server, no live canvas.
Pure offline generation — Python builds the JSON, present_files delivers it.

## Planes

```
control:   SKILL.md (this file) — routing only
data:      registry/  — schemas, palettes, constants, patterns
execution: scripts/generate.py — builds .excalidraw JSON
verify:    tests/smoke.sh
```

## Read order

```yaml
read_first: registry/constants.json
then:       registry/element-schema.json
then:       registry/colors.json
then:       registry/layout-patterns.yaml
then:       registry/gotchas.json
```

## Decision tree

```yaml
input_is_image_or_ascii_or_description:
  action: "parse → plan elements → run scripts/generate.py → present_files"

input_is_existing_excalidraw:
  action: "read file → transform/augment elements → write new file → present_files"

input_wants_mcp_live_canvas:
  action: "tell user: this skill generates offline .excalidraw files; for live canvas use excalidraw-toolkit"

output_file_name:
  rule: "snake_case description + .excalidraw; e.g. arch.excalidraw"

roughness_default:
  rule: "roughness=1 (artist/hand-drawn) unless user says clean/smooth → roughness=0"

font_default:
  rule: "fontFamily=1 (Virgil) for hand-drawn; fontFamily=5 (Excalifont) for clean"

arrow_routing:
  rule: "use explicit points array; calculate from element bboxes; startBinding/endBinding only when tight snap needed"

container_text:
  rule: "text inside shape: containerId on text, boundElements entry on shape"

z_order:
  rule: "elements array order: zone rects FIRST → shapes → arrows → standalone text LAST"

index_field:
  rule: "ascending strings: backgrounds='Za','Zb'; shapes='a1','a2'; arrows='b1','b2'; text='c1','c2'"
```

## Execution steps

```yaml
1: read registry/constants.json + registry/element-schema.json + registry/colors.json
2: read registry/layout-patterns.yaml + registry/gotchas.json
3: plan layout (zones → shapes → arrows → text labels)
4: write/run scripts/generate.py with element definitions
5: validate output with --validate flag
6: present_files the .excalidraw file
```