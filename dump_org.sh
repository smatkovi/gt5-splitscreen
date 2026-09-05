#!/bin/bash
# Liest das Organizer-Objekt und die Auto-Slots aus dem laufenden GT5-Prozess.
#   Aufruf: ./dump_org.sh 0x10002000
# Vorher: GT5 im haengenden Ladebalken stehen lassen.
: "${PS3:?Bitte PS3=<ip> setzen}"
ORG="${1:?Basisadresse des Objekts angeben, z.B. 0x10002000}"

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://$PS3/home.ps3mapi")
[ "$code" = "200" ] || { echo "webMAN antwortet $code - busy? warten oder restart.ps3"; exit 1; }
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }

rd() {  # rd <adresse> <laenge> -> Hexbytes
    curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=$2" \
      | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -$(( ($2+3)/4 )) | tr -d ' ' | tr '\n' ' '
}
w32() { rd "$1" 4 | tr -d ' '; }         # ein 32-Bit-Wort
hx()  { printf '0x%x' $(( $1 )); }

echo "vtable   @ $ORG        : $(w32 $ORG)      (erwartet 016C5AE0)"
CNT_A=$(hx $(( ORG + 0x984 )))
PTR_A=$(hx $(( ORG + 0x234 )))
CNT_H=$(w32 $CNT_A); PTR_H=$(w32 $PTR_A)
echo "slotcount@ $CNT_A : $CNT_H"
echo "slotarray@ $PTR_A : $PTR_H"

CNT=$(( 16#${CNT_H:-0} )); PTR=$(( 16#${PTR_H:-0} ))
[ "$PTR" -eq 0 ] && { echo "Slot-Array-Zeiger ist 0 - Objekt vermutlich falsch."; exit 1; }
[ "$CNT" -gt 16 ] && { echo "Slot-Anzahl $CNT unplausibel - Objekt vermutlich falsch."; exit 1; }

echo "--- Slots (0x640 Abstand) ---"
for ((i=0; i<CNT; i++)); do
    S=$(( PTR + i*0x640 ))
    echo "slot $i @ $(hx $S)  +0x00=$(w32 $(hx $S))  +0x0c=$(w32 $(hx $((S+0xc))))  +0x10=$(w32 $(hx $((S+0x10))))"
done
echo
echo "Fertig gilt ein Slot, wenn +0x0c != 0 UND das erste Byte von +0x10 != 0."
