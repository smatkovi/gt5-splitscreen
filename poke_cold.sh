#!/bin/bash
# Setzt den "+2 -> +3"-Patch, solange der Code kalt ist.
# IM HAUPTMENUE ausfuehren, bevor jemals ein Rennen geladen wurde -
# sonst haelt der I-Cache der PPU die alte Fassung und der Patch wirkt nicht.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
         | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }

poke 0x37b250 3BFF0003   # Slot-Anzahl:  addi r31,r31,2 -> 3
poke 0x379c30 39290003   # Kapazitaet:   addi r9,r9,2   -> 3
for A in 0x37b250 0x379c30; do echo "  $A : $(rd $A)"; done
echo "erwartet: 3BFF0003 / 39290003"
echo
echo "JETZT erst Split-Battle mit Spieler 3 starten."
