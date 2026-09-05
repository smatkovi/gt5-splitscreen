#!/bin/bash
# Liest die Ladeauftraege aus dem laufenden GT5-Prozess.
#   Aufruf: ./dump_jobs.sh [organizer-adresse]     (Standard 0x4FEB9000)
# Im haengenden Ladebalken ausfuehren.
: "${PS3:?Bitte PS3=<ip> setzen}"
ORG=${1:-0x4FEB9000}
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }

w32() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
        | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
hx() { printf '0x%x' $(( $1 )); }

CNT=$(( 16#$(w32 $(hx $(( ORG + 0x984 )) )) ))
DONE=$(( 16#$(w32 $(hx $(( ORG + 0x988 )) )) ))
ARRH=$(w32 $(hx $(( ORG + 0xbd8 )) ))
ARR=$(( 16#$ARRH ))
echo "Slots=$CNT  erzeugte Auftraege=$DONE  Auftragsliste=0x$ARRH"
[ "$ARR" -eq 0 ] && { echo "keine Auftragsliste"; exit 1; }

echo
printf '%-4s %-10s %-10s %-10s %-10s %-10s\n' "job" "+0x18" "+0x24" "+0x28" "+0x2C" "+0x30"
printf '%-4s %-10s %-10s %-10s %-10s %-10s\n' "" "slot2" "slotptr" "slotidx" "?" "organizer"
for ((i=0; i<CNT; i++)); do
    J=$(( ARR + i*0x34 ))
    printf '%-4s %-10s %-10s %-10s %-10s %-10s\n' "$i" \
      "$(w32 $(hx $((J+0x18))))" "$(w32 $(hx $((J+0x24))))" \
      "$(w32 $(hx $((J+0x28))))" "$(w32 $(hx $((J+0x2c))))" \
      "$(w32 $(hx $((J+0x30))))"
done

echo
echo "Abbruchbedingung 0x37e020:  [[org+0x1c]+0x64]"
P=$(w32 $(hx $(( ORG + 0x1c ))))
echo "  org+0x1c = 0x$P"
[ -n "$P" ] && [ "$P" != "00000000" ] && \
  echo "  +0x64    = $(w32 $(hx $(( 16#$P + 0x64 ))))   (ungleich 0 => Auftrag wird verworfen)"
