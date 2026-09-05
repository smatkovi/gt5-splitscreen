#!/bin/bash
# Emulator counterpart of deploy_mod.sh: copy a packed PDIPFS overlay (<mod>-pdipfs, output of
# GTToolsSharp pack) into the RPCS3 game folder instead of uploading it to the PS3.
#   Usage: deploy_mod_rpcs3.sh <mod>-pdipfs            e.g. deploy_mod_rpcs3.sh ~/gt5re/mod_mem-pdipfs
# --remove-destination: never write through an existing file (hardlink safety), always replace.
set -e
OUT="${1:?usage: deploy_mod_rpcs3.sh <mod>-pdipfs}"
DST="$HOME/.config/rpcs3/dev_hdd0/game/BCES00569/USRDIR/PDIPFS"
[ -d "$OUT" ] || { echo "no such dir: $OUT" >&2; exit 1; }
pgrep -x rpcs3 >/dev/null && echo "warning: rpcs3 is running - deploy takes effect at next boot" >&2
find "$OUT" -type f | while read -r f; do
    rel="${f#$OUT/}"
    mkdir -p "$DST/$(dirname "$rel")"
    cp --remove-destination "$f" "$DST/$rel"
    echo "  $rel -> PDIPFS ($(stat -c %s "$f") bytes)"
done
echo "done."
