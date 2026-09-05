#!/bin/bash
# GT5 4P-Mod: Pack-Baum bauen, PDIPFS packen, auf die PS3 schieben.
#   Aufruf:  ./deploy_mod.sh <mod-verzeichnis>       z.B. ./deploy_mod.sh ~/gt5re/mod_w3
# Voraussetzungen: $PS3 gesetzt, $GTTOOLS zeigt auf den GTToolsSharp-Aufruf.
set -e

MOD="${1:?Bitte das Mod-Verzeichnis angeben, z.B. ~/gt5re/mod_w3}"
BASE="$HOME/gt5re"
SRC="$MOD/src/projects/gt5"
PACKDIR="$MOD-pack"
OUT="$MOD-pdipfs"
GTTOOLS="${GTTOOLS:-dotnet $HOME/GTToolsSharp/GTToolsSharp.dll}"

# 1. Pack-Baum: nur die beiden geaenderten .adc, in der Ordnerstruktur des Volumes
rm -rf "$PACKDIR"
mkdir -p "$PACKDIR/projects/gt5/arcade" "$PACKDIR/projects/gt5/race"
cp "$SRC/arcade/arcade.adc" "$PACKDIR/projects/gt5/arcade/"
cp "$SRC/race/race.adc"     "$PACKDIR/projects/gt5/race/"

# 2. Packen. Der Schraegstrich am Ende von -p ist Pflicht:
#    ohne ihn laesst GTToolsSharp unter Linux ein fuehrendes / im Pfad stehen,
#    legt einen zweiten TOC-Eintrag an und das Spiel liest weiter das Original.
rm -rf "$OUT"
$GTTOOLS pack -i "$BASE/update/USRDIR/PDIPFS" -p "$PACKDIR/" -o "$OUT" | tee /tmp/pack.log

echo "--- Pruefung: neue Schluessel muessen 'changed as new' zeigen ---"
grep -i "changed as new" /tmp/pack.log || echo "!! WARNUNG: keine neuen Eintraege - Pfad-Bug?"

# 3. Hochladen: alles was GTToolsSharp ausgegeben hat (Header, TOC, die Dateien)
echo "--- Upload ---"
find "$OUT" -type f | while read -r f; do
    rel="${f#$OUT/}"
    echo -n "  $rel ... "
    curl -s --ftp-create-dirs -T "$f" \
        "ftp://$PS3/dev_hdd0/game/BCES00569/USRDIR/PDIPFS/$rel" && echo ok
done
echo "fertig."
