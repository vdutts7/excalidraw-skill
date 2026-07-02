#!/usr/bin/env zsh
# Assemble installable skill bundle from repo parts (not the git showcase layer).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
NS=excalidraw
MODE=local
OUT_DIR="$ROOT/dist/$NS"
ARCHIVE=0
ARCHIVE_PATH=""
VALIDATE=0
INSTALL_DIR=""
DOWNLOADS=0

usage() {
  cat <<'EOF'
usage: ./pack.sh [options]

Build skill bundle from SKILL.md + registry/ + scripts/ (+ tests/ for local).
Excludes README, examples, .github, and other repo-only files.

Options:
  --cloud          cloud upload surface (omit tests/)
  --downloads      build cloud .skill → ~/Downloads/excalidraw.skill (claude.ai upload)
  --out DIR        output directory (default: dist/excalidraw)
  --archive        write dist/*.skill zip next to bundle parent
  --archive-path F explicit .skill zip path (implies --archive)
  --validate       run SKILL_BUNDLE_VALIDATOR on bundle if set
  --install [DIR]  copy bundle (default: ~/.agents/skills/excalidraw)
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cloud) MODE=cloud; shift ;;
    --downloads)
      DOWNLOADS=1
      MODE=cloud
      ARCHIVE=1
      ARCHIVE_PATH="${HOME}/Downloads/${NS}.skill"
      shift
      ;;
    --out) OUT_DIR="${2:?}"; shift 2 ;;
    --archive) ARCHIVE=1; shift ;;
    --archive-path) ARCHIVE=1; ARCHIVE_PATH="${2:?}"; shift 2 ;;
    --validate) VALIDATE=1; shift ;;
    --install)
      if [[ "${2:-}" == --* || -z "${2:-}" ]]; then
        INSTALL_DIR="${HOME}/.agents/skills/${NS}"
      else
        INSTALL_DIR="$2"
        shift
      fi
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

OUT_DIR="$(python3 -c "import os,sys; print(os.path.abspath(sys.argv[1]))" "$OUT_DIR")"
DIST_PARENT="$(dirname "$OUT_DIR")"
mkdir -p "$DIST_PARENT"

TEMP_OUT=""
if [[ "$DOWNLOADS" -eq 1 ]]; then
  TEMP_OUT="$(mktemp -d)/$NS"
  OUT_DIR="$TEMP_OUT"
  DIST_PARENT="$(dirname "$OUT_DIR")"
fi

parts=(SKILL.md registry scripts)
[[ "$MODE" == local ]] && parts+=(tests)

if [[ -d "$OUT_DIR" ]]; then
  /usr/bin/trash "$OUT_DIR"
fi
mkdir -p "$OUT_DIR"

for part in "${parts[@]}"; do
  src="$ROOT/$part"
  [[ -e "$src" ]] || { echo "pack: missing $part" >&2; exit 1; }
  if [[ -d "$src" ]]; then
    rsync -a --exclude '.DS_Store' --exclude 'pack-manifest.json' "$src/" "$OUT_DIR/$part/"
  else
    cp "$src" "$OUT_DIR/$part"
  fi
done

python3 - "$OUT_DIR" "$NS" "$MODE" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(sys.argv[1])
ns = sys.argv[2]
mode = sys.argv[3]
files = []
for f in sorted(out.rglob("*")):
    if f.is_file() and not f.name.startswith("."):
        files.append(f"{ns}/{f.relative_to(out).as_posix()}")
manifest = {
    "name": ns,
    "skill_type": "F",
    "pack_kind": "local" if mode == "local" else "upload",
    "packed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "files": files,
    "cli": "pack.sh",
}
reg = out / "registry"
reg.mkdir(parents=True, exist_ok=True)
(reg / "pack-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"pack-manifest: {len(files)} files")
PY

if [[ "$ARCHIVE" -eq 1 ]]; then
  if [[ -n "$ARCHIVE_PATH" ]]; then
    archive="$(python3 -c "import os,sys; print(os.path.expanduser(os.path.abspath(sys.argv[1])))" "$ARCHIVE_PATH")"
  else
    suffix=$([[ "$MODE" == local ]] && echo local || echo cloud)
    archive="$DIST_PARENT/${NS}.${suffix}.skill"
  fi
  mkdir -p "$(dirname "$archive")"
  [[ -f "$archive" ]] && /usr/bin/trash "$archive"
  python3 - "$OUT_DIR" "$NS" "$archive" <<'PY'
import sys
import zipfile
from pathlib import Path

out = Path(sys.argv[1])
ns = sys.argv[2]
archive = Path(sys.argv[3])
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(out.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            zf.write(f, f"{ns}/{f.relative_to(out).as_posix()}")
print(f"archive: {archive}")
PY
  if [[ "$DOWNLOADS" -eq 1 ]]; then
    echo "claude.ai upload: $archive"
  fi
fi

if [[ "$VALIDATE" -eq 1 ]]; then
  VALIDATE_BIN="${SKILL_BUNDLE_VALIDATOR:-}"
  if [[ -z "$VALIDATE_BIN" || ( ! -x "$VALIDATE_BIN" && ! -f "$VALIDATE_BIN" ) ]]; then
    echo "pack: --validate skipped (set SKILL_BUNDLE_VALIDATOR)" >&2
  else
    bash "$VALIDATE_BIN" --root "$OUT_DIR" --strict --l3
  fi
fi

if [[ -n "$INSTALL_DIR" ]]; then
  mkdir -p "$(dirname "$INSTALL_DIR")"
  if [[ -d "$INSTALL_DIR" ]]; then
    /usr/bin/trash "$INSTALL_DIR"
  fi
  rsync -a "$OUT_DIR/" "$INSTALL_DIR/"
  echo "installed: $INSTALL_DIR"
fi

[[ -n "$TEMP_OUT" && -d "$TEMP_OUT" ]] && /usr/bin/trash "$(dirname "$TEMP_OUT")"

if [[ "$DOWNLOADS" -eq 1 ]]; then
  echo "done: upload ${ARCHIVE_PATH/#$HOME/~} at claude.ai → Settings → Skills"
else
  echo "bundle: $OUT_DIR ($MODE)"
fi
