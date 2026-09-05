#!/bin/bash
# Instrumentierungs-Cave fuer 0x381e54: schreibt pro Slot-Index nach 0x1949000+idx*16
#   [count, slot+0x28, slot+4, state]  bei jedem Aufruf (letzter Wert bleibt stehen).
#
#   ~/gt5re/cave_deploy.sh apply   - Cave + Hook setzen, Log nullen (KALT, im Hauptmenue!)
#   ~/gt5re/cave_deploy.sh off     - Hook zuruecksetzen (Cave bleibt harmlos liegen)
#
# Ablauf: GT5 frisch starten -> Hauptmenue -> apply -> Split-Battle mit Spieler 3
#         -> haengen lassen -> ~/gt5re/cave_read.sh
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
         | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }

if [ "$1" = "off" ]; then
    poke 0x00381ec8 801A0028
    echo "Hook zurueckgesetzt: 0x00381ec8 = $(rd 0x00381ec8)   (Original 801A0028)"
    exit 0
fi

# 1. Cave-Code schreiben
while read -r a w; do [ -z "$a" ] && continue; poke "$a" "$w"; done <<'EOF'
0x01580ca0 F961FFF8
0x01580ca4 F981FFF0
0x01580ca8 3D600194
0x01580cac 616B9000
0x01580cb0 57CC2036
0x01580cb4 7D6B6214
0x01580cb8 818B0000
0x01580cbc 398C0001
0x01580cc0 918B0000
0x01580cc4 819A0028
0x01580cc8 918B0004
0x01580ccc 819A0004
0x01580cd0 918B0008
0x01580cd4 819A04F4
0x01580cd8 918B000C
0x01580cdc E961FFF8
0x01580ce0 E981FFF0
0x01580ce4 801A0028
0x01580ce8 4AE011E4
EOF
# 2. Log-Puffer nullen (4 Slots x 16 Byte)
for i in 0 4 8 12 16 20 24 28 32 36 40 44 48 52 56 60; do
    poke $(printf '0x%x' $((0x1949000+i))) 00000000
done
# 3. Hook setzen (zuletzt)
poke 0x00381ec8 491FEDD8
echo "Cave gesetzt, Hook @ 0x00381ec8 = $(rd 0x00381ec8)   (soll 491FEDD8)"
echo "Jetzt Split-Battle mit Spieler 3 starten."
