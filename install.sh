#!/usr/bin/env bash
# One-shot install: clone (if needed) → pack cloud .skill → ~/Downloads/excalidraw.skill
set -euo pipefail

REPO="https://github.com/vdutts7/excalidraw-skill.git"
REF="${EXCALIDRAW_SKILL_REF:-main}"

if [[ -n "${EXCALIDRAW_SKILL_ROOT:-}" && -f "${EXCALIDRAW_SKILL_ROOT}/pack.sh" ]]; then
  exec "${EXCALIDRAW_SKILL_ROOT}/pack.sh" --downloads
fi

_script="${BASH_SOURCE[0]:-$0}"
if [[ -f "$_script" ]]; then
  _dir="$(cd "$(dirname "$_script")" && pwd)"
  if [[ -f "$_dir/pack.sh" && "$_dir" != /dev/fd/* && "$_dir" != /proc/* ]]; then
    exec "$_dir/pack.sh" --downloads
  fi
fi

command -v git >/dev/null || { echo "install: need git" >&2; exit 1; }

TMP="$(mktemp -d)"
trap '/usr/bin/trash "$TMP" 2>/dev/null || true' EXIT

git clone --depth 1 --branch "$REF" "$REPO" "$TMP/excalidraw-skill"
exec "$TMP/excalidraw-skill/pack.sh" --downloads
