#!/bin/bash
# Gleicht Slot 2 an die fertigen Slots an: +0x10=1, +0x12=0, +0x1D=1
#   Aufruf: ./fix3rd.sh 0x42402010      (Slot-Array-Adresse)
# Im haengenden Ladebalken ausfuehren.
: "${PS3:?Bitte PS3=<ip> setzen}"
ARR="${1:?Slot-Array-Adresse angeben}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
S=$(( ARR + 2*0x640 ))
A10=$(printf '0x%x' $(( S + 0x10 )))
A1C=$(printf '0x%x' $(( S + 0x1c )))

rd() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
       | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }

echo "vorher : $A10=$(rd $A10)  $A1C=$(rd $A1C)"
poke $A10 01000000     # +0x10=01, +0x11=00, +0x12=00, +0x13=00
poke $A1C 00010000     # +0x1C=00, +0x1D=01, +0x1E=00, +0x1F=00
echo "nachher: $A10=$(rd $A10)  $A1C=$(rd $A1C)"
echo "(Slot 0 zum Vergleich: 01000000 / 00010000)"
