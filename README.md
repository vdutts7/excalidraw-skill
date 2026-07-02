<p align="center">
  <img src="https://raw.githubusercontent.com/vdutts7/squircle/main/webp/excalidraw.webp" alt="logo" width="80" height="80" />
  <img src="https://raw.githubusercontent.com/vdutts7/squircle/main/webp/claude.webp" alt="logo" width="80" height="80" />
  <img src="https://raw.githubusercontent.com/vdutts7/squircle/main/webp/json.webp" alt="logo" width="80" height="80" />
</p>
<h1 align="center">excalidraw-skill</h1>
<p align="center"><em>agent skill that ships valid <code>.excalidraw</code> v2 JSON offline</em></p>

---

<p align="center">
  <img src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1782953487/gh-repos/excalidraw-skill/excalidraw-skill-demo.gif" alt="excalidraw-skill demo" width="720" />
</p>

| Path | You get | Verdict |
|---|---|---|
| Mermaid / SVG / PNG only | pretty render, not editable in Excalidraw | ❌ dead end for hand-drawn edits |
| Live MCP canvas | browser session, extra deps | ❌ wrong when you need a file artifact |
| `/excalidraw` + `scripts/generate.py` | [`three_tier.excalidraw`](examples/outputs/three_tier.excalidraw) drag + drop + open in `excalidraw.com` | ✅ canonical JSON- no MCP |

Same utterance in agent chat: *"draw a 3-tier stack: CDN, API, Postgres + Redis as excalidraw"*

| Artifact | Honest extension |
|---|---|
| Plan the agent writes | `examples/plans/three_tier.json` |
| File you open | [`examples/outputs/three_tier.excalidraw`](examples/outputs/three_tier.excalidraw) |

## Issue

❌ **Raster / vector export only**

1. PNG/SVG looks fine in README
2. cannot drag boxes, re-route arrows, or fork layout in Excalidraw

❌ **Hand-built JSON**

1. `points[0]` must be `[0,0]`; `appState` + `files` required or excalidraw.com rejects load
2. zone z-order, `containerId`, `fontFamily` ints: easy to ship invalid v2

❌ **MCP live canvas for a file deliverable**

1. session-bound
2. not the artifact you attach to a PR or doc

## Setup

```bash
npx skills add vdutts7/excalidraw-skill -g -y
```

- Skill lands in agent skill dirs (`.cursor/skills/`, `.agents/skills/`, etc.) per [`skills` CLI](https://github.com/vercel-labs/skills)

## Output

`.excalidraw` v2 JSON fields: `type`, `version`, `elements`, `appState`, `files`

1. drag+drop `*.excalidraw` file into [Excalidraw](https://excalidraw.com) > Load from file
2. check samples in [`examples/outputs/`](examples/outputs/)

### Agent

```text
/excalidraw draw a 3-tier stack: cdn -> api -> postgres + redis
```

### Generator

```bash
python3 scripts/generate.py examples/plans/pipeline.json \
  --out examples/outputs/pipeline.excalidraw
python3 scripts/generate.py --validate examples/outputs/pipeline.excalidraw
```

### Examples

```bash
./examples/run-all.sh
```

## Gotchas

| symptom | fix | stability | why |
|---|---|---|---|
| excalidraw.com blank load | add `appState` + `files` on root doc | stable | v2 loader requires both fields |
| arrow geometry wrong | `points[0]` always `[0,0]`; offset via element `x`,`y` | stable | points are relative to anchor |
| label clipped between boxes | >= 150px gap on labeled arrows | stable | label needs horizontal clearance |
| text not inside shape | set `containerId` + shape `boundElements` | stable | binding is bidirectional |

## Tools used

<img src="https://img.shields.io/badge/Excalidraw-6965db?style=for-the-badge&logo=excalidraw&logoColor=white" alt="Excalidraw"/>

## Contact

<a href="https://vd7.io">
<img src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1773910810/readme-badges/readme-badge-vd7.png" alt="vd7.io" height="40" />
</a>
&nbsp;
<a href="https://x.com/vdutts7">
<img src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1773910817/readme-badges/readme-badge-x.png" alt="/vdutts7" height="40" />
</a>
