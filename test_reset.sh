#!/bin/bash
# EXPERIMENT: die Reset-Verzweigung in 0x381e54 ausschalten.
# 0x381f6c  blt cr7, 0x381f94  (419C0028)  ->  nop (60000000)
# Damit rueckt der dritte Slot vor (Zustand 21), statt auf 22 zurueckgeworfen zu werden,
# wenn viewport_count (0x379bf0 = 2) < slot_count (3).
#
# IM HAUPTMENUE ausfuehren (kalt, I-Cache), dann Split-Battle mit Spieler 3.
# Rollback: Argument "off" oder GT5 neu starten.
#
# Falls test_spin1 (0x394388) noch gesetzt ist: erst GT5 neu starten, damit wir
# sauber NUR diesen Patch testen.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
         | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
if [ "$1" = "off" ]; then
    poke 0x381f6c 419C0028
    echo "zurueckgesetzt: 0x381f6c = $(rd 0x381f6c)   (Original 419C0028)"
else
    poke 0x381f6c 60000000
    echo "gesetzt: 0x381f6c = $(rd 0x381f6c)   (nop = 60000000)"
    echo "Jetzt Split-Battle mit Spieler 3 starten."
fi
