#!/bin/bash
# TEIL B - im haengenden Ladebalken ausfuehren.
: "${PS3:?Bitte PS3=<ip> setzen}"
SCRATCH=$(cat /tmp/gt5_scratch 2>/dev/null)
[ -n "$SCRATCH" ] || { echo "keine Ablage gemerkt - erst leak_a.sh laufen lassen"; exit 1; }

PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
w32() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
        | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }

VAL=$(w32 $SCRATCH)
echo "Ablage $SCRATCH : $VAL"

echo "getLoadedCarCount wiederherstellen..."
poke 0x382cc8 80030984
poke 0x382ccc 39000000
poke 0x382cd0 2F800000
poke 0x382cd4 409D0048

if [ "$VAL" != "00000000" ] && [ -n "$VAL" ]; then
    echo "Weiter mit:  ~/gt5re/dump_org.sh 0x$VAL"
else
    echo "Nichts geschrieben - entweder wurde getLoadedCarCount nicht erreicht,"
    echo "oder der I-Cache haelt weiterhin die alte Fassung."
fi
