#!/bin/bash
# ROOT Stufe 1: Load-Fix (cave4) + Viewport-Zahl 0x379bf0 auf 3 (0x379c30: +2 -> +3).
# Ziel: nachgelagerte Stufen (Kurs-Eintritt) sollen alle drei Autos verarbeiten.
#   ~/gt5re/root1_deploy.sh apply | off
# KALT im Hauptmenue, dann Split-Battle mit Spieler 3.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
if [ "$1" = "off" ]; then
    poke 0x00381fb0 38800016            # cave4-Hook zurueck
    poke 0x379c30 39290002        # Viewport-Zahl zurueck
    echo "zurueckgesetzt: Hook=$(rd 0x00381fb0) (soll 38800016), 0x379c30=$(rd 0x379c30) (soll 39290002)"
    exit 0
fi
# cave4-Code
while read -r a w; do [ -z "$a" ] && continue; poke "$a" "$w"; done <<'EOF'
0x01580d80 3C804240
0x01580d84 60842C90
0x01580d88 7C1A2000
0x01580d8c 40820018
0x01580d90 809A04F4
0x01580d94 2C04000B
0x01580d98 4082000C
0x01580d9c 38600000
0x01580da0 4AE012E4
0x01580da4 38800016
0x01580da8 4AE0120C
EOF
poke 0x00381fb0 491FEDD0                    # cave4-Hook
poke 0x379c30 39290003            # Viewport-Zahl 2 -> 3
echo "Load-Fix Hook @ 0x00381fb0 = $(rd 0x00381fb0)  (soll 491FEDD0)"
echo "Viewport-Zahl 0x379c30 = $(rd 0x379c30)  (soll 39290003)"
echo "Jetzt Split-Battle mit Spieler 3 starten."
