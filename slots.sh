#!/bin/bash
# Vergleicht die drei Auto-Slots und die daran haengenden Auto-Objekte.
#   Aufruf: ./slots.sh 0x42402010     (Slot-Array-Zeiger aus dump_org.sh)
: "${PS3:?Bitte PS3=<ip> setzen}"
ARR="${1:?Slot-Array-Adresse angeben}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }

dump() {  # dump <adresse> <laenge>
    curl -s --max-time 25 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=$2" \
      | sed 's/<br>/\n/g' \
      | grep -oiE '^[0-9A-F]{8}  ([0-9A-F]{2} )+' 
}
w32() { dump "$1" 4 | head -1 | awk '{print $2$3$4$5}'; }

for i in 0 1 2; do
    S=$(printf '0x%x' $(( ARR + i*0x640 )))
    echo "=== slot $i @ $S ==="
    dump $S 96
done

echo
for i in 0 1 2; do
    S=$(printf '0x%x' $(( ARR + i*0x640 + 0xc )))
    CAR=$(w32 $S)
    echo "=== slot $i -> Auto-Objekt 0x$CAR ==="
    [ -n "$CAR" ] && [ "$CAR" != "00000000" ] && dump 0x$CAR 96
done
