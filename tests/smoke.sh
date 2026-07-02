#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

GEN="$SKILL_ROOT/scripts/generate.py"

TMP=$(mktemp -d)

trap "/usr/bin/trash $TMP" 2>/dev/null EXIT

echo "=== excalidraw skill smoke tests ==="

# 1. Skeleton output is valid JSON with required root fields

echo -n "[1] skeleton output ... "

python3 "$GEN" --skeleton > "$TMP/skeleton.json"

python3 -c "

import json,sys

d=json.load(open('$TMP/skeleton.json'))

assert d['type']=='excalidraw','type'

assert d['version']==2,'version'

assert 'appState' in d,'appState'

assert 'files' in d,'files'

assert isinstance(d['elements'],list),'elements'

print('PASS')

"

# 2. Validate a minimal plan with all element kinds

cat > "$TMP/plan.json" << 'EOF'

{

  "output": "",

  "elements": [

    {"kind":"zone",    "id":"z1",  "x":0,   "y":0,   "w":600, "h":300, "label":"Backend"},

    {"kind":"rect",    "id":"r1",  "x":40,  "y":60,  "w":220, "h":120, "bg":"#a5d8ff", "stroke":"#1971c2", "label":"API Server"},

    {"kind":"diamond", "id":"d1",  "x":320, "y":80,  "w":200, "h":120, "bg":"#fff3bf", "stroke":"#fab005", "label":"Decision"},

    {"kind":"ellipse", "id":"e1",  "x":580, "y":80,  "w":180, "h":120, "bg":"#b2f2bb", "stroke":"#2f9e44"},

    {"kind":"text",    "id":"t1",  "x":40,  "y":10,  "w":200, "h":30,  "text":"Title", "fontSize":20},

    {"kind":"arrow",   "id":"a1",  "x":260, "y":120, "dx":60, "dy":0,  "stroke":"#1971c2", "label":"REST"}

  ]

}

EOF

echo -n "[2] plan execution ... "

python3 "$GEN" "$TMP/plan.json" --out "$TMP/out.excalidraw" 2>/dev/null

python3 -c "

import json

d=json.load(open('$TMP/out.excalidraw'))

els=[e for e in d['elements'] if not e.get('isDeleted')]

assert len(els)>=6, f'expected >=6 elements, got {len(els)}'

types={e['type'] for e in els}

assert 'rectangle' in types

assert 'arrow' in types

assert 'text' in types

print('PASS')

"

# 3. validate command on the output

echo -n "[3] --validate on generated file ... "

python3 "$GEN" --validate "$TMP/out.excalidraw"

# 4. Check required registry files exist

echo -n "[4] registry files present ... "

for f in constants.json element-schema.json colors.json layout-patterns.yaml gotchas.json; do

  [[ -f "$SKILL_ROOT/registry/$f" ]] || { echo "MISSING: $f"; exit 1; }

done

echo "PASS"

# 5. Arrow points[0]=[0,0] invariant

echo -n "[5] arrow points invariant ... "

python3 -c "

import json

d=json.load(open('$TMP/out.excalidraw'))

for el in d['elements']:

    if el.get('type')=='arrow' and not el.get('isDeleted'):

        assert el['points'][0]==[0,0], f'arrow {el[\"id\"]} points[0] != [0,0]: {el[\"points\"][0]}'

print('PASS')

"

# 6. No duplicate IDs

echo -n "[6] no duplicate IDs ... "

python3 -c "

import json

d=json.load(open('$TMP/out.excalidraw'))

ids=[e['id'] for e in d['elements'] if not e.get('isDeleted')]

assert len(ids)==len(set(ids)), f'duplicate IDs: {[x for x in ids if ids.count(x)>1]}'

print('PASS')

"

echo ""

echo "=== ALL SMOKE TESTS PASSED ==="

