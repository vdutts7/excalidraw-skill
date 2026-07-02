<p align="center">
  <img src="https://raw.githubusercontent.com/vdutts7/squircle/main/webp/excalidraw.webp" alt="logo" width="80" height="80" />
  <img src="https://raw.githubusercontent.com/vdutts7/squircle/main/webp/claude.webp" alt="logo" width="80" height="80" />
</p>
<h1 align="center">/excalidraw skill</h1>
<p align="center"><em>agent skill for making instant Excalidraw diagrams- for system design, mind maps, etc</em></p>

<p align="center">
<a href="https://res.cloudinary.com/ddyc1es5v/raw/upload/v1782970520/gh-repos/excalidraw-skill/excalidraw.skill" download="excalidraw.skill">
<img src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1782972571/readme-badges/readme-badge-install.png" alt="install /excalidraw" height="56" />
</a>
</p>

---

<p align="center">
  <img
    src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1782954015/gh-repos/excalidraw-skill/excalidraw-skill-demo.gif"
    alt="excalidraw-skill demo"
    width="720"
  />
</p>

| | path | you get | verdict |
|:---:|---|---|---|
| <img src="https://raw.githubusercontent.com/vdutts7/squircle/refs/heads/main/webp/mermaid.webp" width="40" height="40" alt="Mermaid" /> | <ul><li>Mermaid</li><li>SVG</li><li>PNG only</li></ul> | <ul><li>pretty render in README</li><li>not editable on `excalidraw.com`</li><li>can't drag boxes, reroute arrows, fork layout</li></ul> | ❌<br/><br/>dead end for hand-drawn edits |
| <img src="https://raw.githubusercontent.com/vdutts7/squircle/refs/heads/main/webp/json.webp" width="40" height="40" alt="JSON" /> | <ul><li>hand-built JSON</li><li>raw v2 by hand</li></ul> | <ul><li>`points[0]` must be `[0,0]`</li><li>`appState` + `files` required or load fails</li><li>`containerId`, `fontFamily` ints, zone z-order: easy invalid v2</li></ul> | ❌<br/><br/>easy to ship broken files |
| <img src="https://raw.githubusercontent.com/vdutts7/squircle/refs/heads/main/webp/mcp.webp" width="40" height="40" alt="MCP" /> | <ul><li>Live MCP canvas</li></ul> | <ul><li>browser session</li><li>extra deps</li><li>session-bound</li><li>not a file you attach to a PR or doc</li></ul> | ❌<br/><br/>wrong when you need a file artifact |
| <img src="https://raw.githubusercontent.com/vdutts7/squircle/refs/heads/main/webp/excalidraw.webp" width="40" height="40" alt="Excalidraw" /> | <ul><li>`/excalidraw`</li><li>`scripts/generate.py`</li></ul> | <ul><li>[`three_tier.excalidraw`](examples/outputs/three_tier.excalidraw) drag + drop</li><li>open in `excalidraw.com`</li></ul> | ✅<br/><br/>canonical JSON- no MCP |


| Artifact | Honest extension |
|---|---|
| plan the agent writes | `examples/plans/three_tier.json` |
| file you open | [`examples/outputs/three_tier.excalidraw`](examples/outputs/three_tier.excalidraw) |

## Setup

<p align="center">
<a href="https://res.cloudinary.com/ddyc1es5v/raw/upload/v1782970520/gh-repos/excalidraw-skill/excalidraw.skill" download="excalidraw.skill">
<img src="https://res.cloudinary.com/ddyc1es5v/image/upload/v1782972571/readme-badges/readme-badge-install.png" alt="install /excalidraw" height="56" />
</a>
</p>

A. click `Install` → `excalidraw.skill` → upload to: `claude.ai`, cloud platforms, etc
- or `mv excalidraw.skill excalidraw.zip`, then unzip locally for → Codex, Cursor, Claude Code, Pi, OpenClaw, etc

B. or from source:

```bash
curl -fsSL https://raw.githubusercontent.com/vdutts7/excalidraw-skill/main/install.sh | bash
```

## Output

`*.excalidraw` file with v2 JSON fields:
-`type`
-`version`
-`elements`
-`appState`
-`files`

1. drag + drop `*.excalidraw` file into → [Excalidraw](https://excalidraw.com) > `Load from file`
2. check → [`examples/outputs/`](examples/outputs/)


### Generator

```bash
python3 scripts/generate.py examples/plans/pipeline.json \
  --out examples/outputs/pipeline.excalidraw

python3 scripts/generate.py --validate examples/outputs/pipeline.excalidraw
```

### Usage

**User:**
```markdown
/excalidraw draw a 3-tier stack: cdn -> api -> postgres + redis
```

### Ex

```bash
./examples/run-all.sh
```

## Gotchas

| symptom | fix | stability | why |
|---|---|---|---|
| `excalidraw.com` blank load | add `appState` + `files` on root doc | stable | v2 loader requires both fields |
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
