#!/bin/bash
# Schritt 1: herausfinden, welche Speicherbereiche im GT5-Prozess ueberhaupt gemappt sind.
# Schritt 2: in den gemappten Bereichen nach dem Organizer-Objekt suchen.
#
# Vorher: GT5 starten, Split-Battle mit Spieler 3, im haengenden Ladebalken stehen lassen.
# Achtung: eine unbegrenzte Suche blockiert webMANs einspurigen Webserver (503 Server is Busy).

: "${PS3:?Bitte PS3=<ip> setzen}"

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://$PS3/home.ps3mapi")
[ "$code" = "200" ] || { echo "webMAN antwortet $code - noch busy? warten oder Konsole neu starten."; exit 1; }

PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "FEHLER: kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"

echo "=== Schritt 1: welche Bereiche sind gemappt? ==="
MAPPED=()
for A in 00010000 00300000 01000000 01950000 02000000 02950000 03000000 04000000 \
         05000000 06000000 07000000 08000000 0A000000 0C000000 0E000000 0F000000 \
         10000000 18000000 20000000 28000000 30000000 40000000; do
    n=$(curl -s --max-time 15 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=0x$A&len=16" \
        | grep -coiE '\b[0-9A-F]{2} [0-9A-F]{2} ')
    if [ "$n" -gt 0 ]; then echo "  0x$A  gemappt"; MAPPED+=("$A"); else echo "  0x$A  -"; fi
done

echo "=== Schritt 2: Suche nach vtable 016C5AE0 in den gemappten Bereichen ==="
for A in "${MAPPED[@]}"; do
    echo -n "  ab 0x$A -> "
    curl -s --max-time 90 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=0x$A&find=016C5AE0" \
      | grep -oiE '\b[0-9A-F]{8}\b' | sed -n '4p'
    sleep 1
done
