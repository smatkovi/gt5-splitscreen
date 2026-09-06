#!/bin/bash
# Copy a built script mod (output of tools/build_mod.sh) into both release folders:
#   mod/openadhoc-split.diff (git diff of the mod clone vs. the OpenAdhoc reference, EOL-insensitive),
#   mod/arcade.adc, mod/race.adc, mod/pdipfs/** ; then rebuild the release tarballs.
#   Usage: update_release_mod.sh <mod-dir>      e.g. update_release_mod.sh ~/gt5re/mod_sel
set -e
MOD="${1:?usage: update_release_mod.sh <mod-dir>}"
BASE="$HOME/gt5re"
[ -d "$MOD/.git" ] && [ -d "$MOD-pdipfs" ] || { echo "not a mod build: $MOD" >&2; exit 1; }
for R in "$BASE/release/3p" "$BASE/release/4p"; do
    git -C "$MOD" diff --ignore-space-at-eol -- src/projects/gt5 > "$R/mod/openadhoc-split.diff"
    cp "$MOD/src/projects/gt5/arcade/arcade.adc" "$MOD/src/projects/gt5/race/race.adc" "$R/mod/"
    rm -rf "$R/mod/pdipfs"; mkdir -p "$R/mod/pdipfs"; cp -r "$MOD-pdipfs/." "$R/mod/pdipfs/"
    echo "$R/mod: $(wc -l < "$R/mod/openadhoc-split.diff") diff lines, $(find "$R/mod/pdipfs" -type f | wc -l) overlay files"
done
for n in 3 4; do
    rm -f "$BASE/release/gt5-${n}p-release.tar.gz"
    tar czf "$BASE/release/gt5-${n}p-release.tar.gz" -C "$BASE/release" ${n}p
done
ls -la "$BASE"/release/*.tar.gz
