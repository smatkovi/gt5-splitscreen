#!/bin/bash
# ISOLATIONSTEST: nur Fenster[2] anlegen+konstruieren+wegwerfen, sonst alles Original.
# Testet, ob der Fenster-Konstruktor 0x469320 mit Index 2 absturzfrei ist.
# Mit NORMALEM 2-Spieler-Split testen (wenigste Variablen).
#   ~/gt5re/ctortest.sh apply | off
# KALT im Hauptmenue, dann normales 2P-Split-Battle starten.
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
if [ "$1" = "off" ]; then poke 0x00462124 39200001; echo "Hook zurueck: 0x00462124 = $(rd 0x00462124) (orig 39200001)"; exit 0; fi
while read -r a w; do [ -z "$a" ] && continue; poke "$a" "$w"; done <<'EOF'
0x01580e40 38600740
0x01580e44 4B640B31
0x01580e48 7C7E1B78
0x01580e4c 38800002
0x01580e50 7FC3F378
0x01580e54 4AEE84CD
0x01580e58 3D000194
0x01580e5c 61087100
0x01580e60 93C80000
0x01580e64 39200001
0x01580e68 38000000
0x01580e6c 913D0030
0x01580e70 913D002C
0x01580e74 3D200180
0x01580e78 39600000
0x01580e7c 981D0039
0x01580e80 981D0034
0x01580e84 981D0035
0x01580e88 981D0036
0x01580e8c 981D0037
0x01580e90 981D0038
0x01580e94 9169D0B4
0x01580e98 981D0018
0x01580e9c 4AEE12C0
EOF
poke 0x00462124 4911ED1C
echo "Cave gesetzt, Hook @ 0x00462124 = $(rd 0x00462124) (soll 4911ED1C)"
echo "Jetzt NORMALES 2-Spieler-Split-Battle starten (kein Spieler 3)."
