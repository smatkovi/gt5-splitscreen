#!/bin/bash
# Resetter-Cave: loggt den Aufrufer (LR), der Zustand 22 auf Slot 2 (0x42402c90) schreibt.
# LOG @ 0x1949080: +0 = Aufrufer-LR, +4 = Zaehler.
#   ~/gt5re/cave3_deploy.sh apply | off
# KALT im Hauptmenue anwenden, dann Split-Battle mit Spieler 3.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
if [ "$1" = "off" ]; then poke 0x003b87a8 F821FF51; echo "Hook zurueck: 0x003b87a8 = $(rd 0x003b87a8)"; exit 0; fi
while read -r a w; do [ -z "$a" ] && continue; poke "$a" "$w"; done <<'EOF'
0x01580d00 2C040016
0x01580d04 40820040
0x01580d08 F961FFF8
0x01580d0c F981FFF0
0x01580d10 3D604240
0x01580d14 616B2C90
0x01580d18 7C035800
0x01580d1c 40820020
0x01580d20 7D8802A6
0x01580d24 3D600194
0x01580d28 616B9080
0x01580d2c 918B0000
0x01580d30 818B0004
0x01580d34 398C0001
0x01580d38 918B0004
0x01580d3c E961FFF8
0x01580d40 E981FFF0
0x01580d44 F821FF51
0x01580d48 4AE37A64
EOF
poke 0x1949080 00000000; poke 0x1949084 00000000
poke 0x003b87a8 491C8558
echo "Cave3 gesetzt, Hook @ 0x003b87a8 = $(rd 0x003b87a8)  (soll 491C8558)"
echo "Jetzt Split-Battle mit Spieler 3 starten."
