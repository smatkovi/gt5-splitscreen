#!/bin/bash
# Liest den Instrumentierungs-Log aus (0x1949000, 4 Slots x 16 Byte).
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
rd() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
       | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
printf '%-6s %-10s %-12s %-10s %-8s\n' slot count "slot+0x28" "slot+4" state
for i in 0 1 2 3; do
    base=$((0x1949000 + i*16))
    printf '%-6s %-10s %-12s %-10s %-8s\n' "$i" \
      "$(rd $(printf '0x%x' $((base+0))))" \
      "$(rd $(printf '0x%x' $((base+4))))" \
      "$(rd $(printf '0x%x' $((base+8))))" \
      "$(rd $(printf '0x%x' $((base+12))))"
done
