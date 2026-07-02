#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEN="$ROOT/scripts/generate.py"
PLANS="$ROOT/examples/plans"
OUT="$ROOT/examples/outputs"

mkdir -p "$OUT"

for plan in "$PLANS"/*.json; do
  name="$(basename "$plan")"
  echo "[generate] $name"
  python3 "$GEN" "$plan" --out "$OUT/$(python3 -c "import json; print(json.load(open('$plan'))['output'])")"
  python3 "$GEN" --validate "$OUT/$(python3 -c "import json; print(json.load(open('$plan'))['output'])")"
done

echo "[smoke] tests/smoke.sh"
bash "$ROOT/tests/smoke.sh"

echo "=== examples OK ==="
