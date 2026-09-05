#!/bin/bash
PID=$(curl -s "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
echo "pid=$PID"
[ -z "$PID" ] && { echo "FEHLER: kein Spielprozess - laeuft GT5?"; exit 1; }
poke() { curl -s "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
poke 0x37b250 3BFF0003   # Slot-Addend  2 -> 3
poke 0x379c30 39290003   # Cap-Addend   2 -> 3
poke 0x379c44 60000000   # Deckelung auf hword[+0x1a] entfernen (nop)
for A in 0x37b250 0x379c30 0x379c44; do
  echo -n "$A : "
  curl -s "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$A&len=4" \
    | grep -oiE '\b[0-9A-F]{8}\b' | sed -n 3p
done
