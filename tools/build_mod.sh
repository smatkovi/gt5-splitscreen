#!/bin/bash
# Reproducible build of the GT5 3P/4P Adhoc script mod (arcade.adc + race.adc) from a clean
# OpenAdhoc checkout, packed as a PDIPFS overlay.  Mirrors the recipe in doc/gt5-3p-dossier.html.
#   Usage: build_mod.sh <mod-dir-name>        e.g. build_mod.sh mod_x   -> ~/gt5re/mod_x, mod_x-pack, mod_x-pdipfs
# Steps: git clone OpenAdhoc (HEAD is the untouched reference; the working tree is NOT used),
#        patch_arcade_v3.py (split battle with players 3/4, own MCarDriverParameter per entry),
#        patch_race_log_w4.py with MOD_WINDOW_MAX (default 3),
#        cp.checkValid() in CarRoot/CarSplitRoot (GT5 2.17 API), adhoc build, GTToolsSharp pack.
set -e
BASE="$HOME/gt5re"
NAME="${1:?usage: build_mod.sh <mod-dir-name>}"
MOD="$BASE/$NAME"
export MOD_WINDOW_MAX="${MOD_WINDOW_MAX:-3}"
DOTNET="$HOME/.dotnet/dotnet"
ADHOC="$DOTNET --roll-forward Major $BASE/GTAdhocToolchain/GTAdhocToolchain.CLI/bin/Release/net10.0/adhoc.dll"
GTTOOLS="$DOTNET --roll-forward Major $BASE/GTToolsSharp/GTToolsSharp/bin/Release/net9.0/GTToolsSharp.dll"

rm -rf "$MOD" "$MOD-pack" "$MOD-pdipfs"
git clone -q "$BASE/OpenAdhoc" "$MOD"
# older checkouts used *.Ad; the toolchain wants lowercase
(cd "$MOD" && find . -name '*.Ad' -exec bash -c 'mv "$1" "${1%.Ad}.ad"' _ {} \;)
SRC="$MOD/src/projects/gt5"
python3 "$BASE/patch_arcade_v3.py" "$SRC/arcade/arcade.ad"
python3 "$BASE/patch_race_log_w4.py" "$SRC/race"
python3 - "$SRC" <<'PYEOF'
import sys, pathlib
src = pathlib.Path(sys.argv[1])
for f in ('arcade/CarRoot.ad', 'arcade/CarSplitRoot.ad'):
    p = src / f
    t = p.read_text(encoding='utf-8')
    anchor = 'var cp = car.getCP();'
    assert t.count(anchor) == 1, (f, t.count(anchor))
    i = t.index(anchor)
    line_start = t.rfind('\n', 0, i) + 1
    indent = t[line_start:i]
    ins = anchor + '\n' + indent + 'cp.checkValid(); // added in GT5 2.17\n'
    if 'cp.checkValid()' not in t:
        t = t[:i] + ins + t[i + len(anchor):]
        p.write_text(t, encoding='utf-8')
        print('patched', f)
PYEOF
(cd "$SRC/arcade" && $ADHOC build) | tail -3
(cd "$SRC/race" && $ADHOC build) | tail -3
mkdir -p "$MOD-pack/projects/gt5/arcade" "$MOD-pack/projects/gt5/race"
cp "$SRC/arcade/arcade.adc" "$MOD-pack/projects/gt5/arcade/"
cp "$SRC/race/race.adc" "$MOD-pack/projects/gt5/race/"
# trailing slash on -p is mandatory (see deploy_mod.sh)
$GTTOOLS pack -i "$BASE/update/USRDIR/PDIPFS" -p "$MOD-pack/" -o "$MOD-pdipfs" | tee "$MOD-pack/pack.log" | grep -iE 'changed as new|error' || true
echo "built: $MOD-pdipfs"
find "$MOD-pdipfs" -type f -printf '  %8s  %P\n'
