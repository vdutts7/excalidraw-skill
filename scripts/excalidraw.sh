#!/usr/bin/env zsh
# excalidraw entry — delegates to generate.py (plan JSON → .excalidraw v2)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/generate.py" "$@"
