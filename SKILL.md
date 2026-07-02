---
name: excalidraw
description: >
  /excalidraw excalidraw diagram arch ASCII image to excalidraw v2 JSON;
  triggers convert to excalidraw make excalidraw excalidraw file excalidraw style;
  offline via scripts/excalidraw.sh registry/templates LEGO blocks generate script;
  NOT for: /diagram inline SVG mermaid-only PNG-only live MCP canvas
exec_script: scripts/excalidraw.sh
---

# /excalidraw

exec: bash scripts/excalidraw.sh "$@"
- 🟢 exit 0 → present_files
- 🔴 exit ≠0 → STOP
