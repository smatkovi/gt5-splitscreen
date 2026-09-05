#!/bin/bash
# Ermittelt die Adresse des Organizer-Objekts, indem getLoadedCarCount kurzzeitig
# durch einen Stub ersetzt wird, der seinen this-Zeiger nach 0x01948000 schreibt.
#
# Vorher: GT5 starten, Split-Battle mit Spieler 3, im HAENGENDEN LADEBALKEN stehen lassen.
# Dort wird getLoadedCarCount in jeder Schleifeniteration aufgerufen.
#
# Der Stub:
#   lis  r11, 0x0195        3D600195
#   stw  r3, -0x8000(r11)   906B8000     -> schreibt nach 0x01948000
#   li   r3, 0              38600000
#   blr                     4E800020
# Original:
#   80030984 39000000 2F800000 409D0048

: "${PS3:?Bitte PS3=<ip> setzen}"
SCRATCH=0x1948000

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://$PS3/home.ps3mapi")
[ "$code" = "200" ] || { echo "webMAN antwortet $code - busy? warten oder restart.ps3"; exit 1; }
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"

w32() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
        | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }

echo "Scratch vorher      : $(w32 $SCRATCH)   (sollte 00000000 sein)"

echo "Stub setzen..."
poke 0x382cc8 3D600195
poke 0x382ccc 906B8000
poke 0x382cd0 38600000
poke 0x382cd4 4E800020
sleep 3

VAL=$(w32 $SCRATCH)
echo "Scratch nachher     : $VAL   <-- Adresse des Organizer-Objekts"

echo "Original wiederherstellen..."
poke 0x382cc8 80030984
poke 0x382ccc 39000000
poke 0x382cd0 2F800000
poke 0x382cd4 409D0048
echo "getLoadedCarCount wieder original: $(w32 0x382cc8) $(w32 0x382ccc) $(w32 0x382cd0) $(w32 0x382cd4)"

if [ "$VAL" != "00000000" ] && [ -n "$VAL" ]; then
    echo
    echo "Weiter mit:  ~/gt5re/dump_org.sh 0x$VAL"
fi
