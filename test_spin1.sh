#!/bin/bash
# EXPERIMENT: das erste Tor der Ladeschleife (0x394388, "warte bis Element fertig")
# zwingen -> nop. Damit faellt der Handler durch, statt auf 0x4effa0 zu warten.
#
# IM HAUPTMENUE ausfuehren (kalt, wegen I-Cache), bevor je ein Rennen geladen wurde.
# Danach Split-Battle mit Spieler 3.
#
# Erwartung, falls das Element-Warten der Blocker war: Slot 2 laedt durch, Rennen startet
# (evtl. mit halbfertigem 3. Auto). Falls es abstuerzt: Auto-Daten waren echt noch nicht
# da -> Streaming-Problem, nicht Logik. Falls unveraendert haengt: Blocker liegt am
# zweiten Tor (0x394564) -> dann test_spin2.
#
# Rollback: dieses Skript mit ARG "off" erneut aufrufen ODER GT5 neu starten.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
         | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }

if [ "$1" = "off" ]; then
    poke 0x394388 419EFFCC
    echo "zurueckgesetzt: 0x394388 = $(rd 0x394388)   (Original 419EFFCC)"
else
    poke 0x394388 60000000
    echo "gesetzt: 0x394388 = $(rd 0x394388)   (nop = 60000000)"
    echo "Jetzt Split-Battle mit Spieler 3 starten."
fi
