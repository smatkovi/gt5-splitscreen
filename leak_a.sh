#!/bin/bash
# TEIL A - im HAUPTMENUE ausfuehren, bevor ein Rennen geladen wurde.
# Sucht eine freie Ablage und setzt den Stub, solange der Code noch kalt ist
# (die PPU hat einen getrennten I-Cache; eine heisse Funktion behaelt ihre alte Fassung).
: "${PS3:?Bitte PS3=<ip> setzen}"

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://$PS3/home.ps3mapi")
[ "$code" = "200" ] || { echo "webMAN antwortet $code"; exit 1; }
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
echo "pid=$PID"

w32() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
        | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }

echo "--- freie Ablage suchen (muss zweimal hintereinander 0 sein) ---"
SCRATCH=""
for A in 0x19485A0 0x1948400 0x1948800 0x1947000 0x1946000 0x1945000 0x1940000; do
    v1=$(w32 $A); sleep 1; v2=$(w32 $A)
    echo "  $A : $v1 / $v2"
    if [ "$v1" = "00000000" ] && [ "$v2" = "00000000" ]; then SCRATCH=$A; break; fi
done
[ -n "$SCRATCH" ] || { echo "keine freie Ablage gefunden - melde die Werte oben"; exit 1; }
echo "Ablage: $SCRATCH"

# stw r3, D(r11) braucht D als vorzeichenbehaftete 16 Bit -> Basis passend waehlen
BASE=$(( ( $SCRATCH + 0x8000 ) >> 16 ))
DISP=$(( $SCRATCH - (BASE << 16) ))
DISP16=$(( DISP & 0xFFFF ))
LIS=$(printf '3D60%04X' $BASE)
STW=$(printf '906B%04X' $DISP16)
echo "Stub: lis r11,0x$(printf '%04X' $BASE) / stw r3,0x$(printf '%04X' $DISP16)(r11)"

poke 0x382cc8 $LIS
poke 0x382ccc $STW
poke 0x382cd0 38600000
poke 0x382cd4 4E800020
echo "Stub gesetzt: $(w32 0x382cc8) $(w32 0x382ccc) $(w32 0x382cd0) $(w32 0x382cd4)"
echo "$SCRATCH" > /tmp/gt5_scratch
echo
echo "JETZT: Split-Battle mit Spieler 3 starten und im haengenden Ladebalken stehen lassen."
echo "Danach:  ~/gt5re/leak_b.sh"
