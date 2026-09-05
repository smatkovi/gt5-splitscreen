#!/bin/bash
# GT5 3-Fenster-Patch (48 Woerter, capstone-verifiziert).
#   ~/gt5re/patch_windows3.sh apply    - alle Patches setzen (KALT, im Hauptmenue!)
#   ~/gt5re/patch_windows3.sh revert   - Originalbytes zurueckschreiben
#   ~/gt5re/patch_windows3.sh verify   - aktuellen Stand pruefen
#
# ============================ WARNUNG ============================
# Diese Patches lassen die Engine 3 Fenster verarbeiten. Sie SETZEN VORAUS,
# dass bei Fenster-Manager +0x2c ein GUELTIGER Fenster[2]-Zeiger liegt.
# Ohne echtes drittes Fensterobjekt greifen die Schleifen auf window_max
# als Zeiger zu -> SICHERER ABSTURZ. Nicht anwenden, bevor Fenster[2]
# existiert (window[1] duplizieren o.ae.) UND das dritte Auto laedt.
# Ausserdem fehlt die 3-Wege-Kameratabelle; die Ansicht bleibt sonst 2-geteilt.
# ================================================================
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "kein Spielprozess - laeuft GT5?"; exit 1; }
echo "pid=$PID"
poke() { curl -s --max-time 20 "http://$PS3/setmem.ps3mapi?proc=$PID&addr=$1&val=$2" >/dev/null; }
rd()   { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" \
         | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }

read -r -d '' TABLE <<'EOF'
0x45f274 8063002C 80630028
0x45ff50 801D002C 801D0028
0x45f29c 80630030 80630020
0x45ff54 901D0030 901D0020
0x45ff60 901D0030 901D0020
0x460814 2F840000 90830028
0x460818 9083002C 3943001C
0x46081c 419D0014 39000000
0x460820 8123001C 812A0000
0x460824 38000000 7F882000
0x460828 9809000C 38000001
0x46082c 48000010 419C0008
0x460830 8123001C 38000000
0x460834 38000001 9809000C
0x460838 9809000C 394A0008
0x46083c 8003002C 39080001
0x460840 2F800001 2F880003
0x460844 409D0014 409EFFDC
0x460848 81230024 4E800020
0x46084c 38000001 60000000
0x460850 9809000C 60000000
0x460854 4E800020 60000000
0x460858 81230024 60000000
0x46085c 38000000 60000000
0x460860 9809000C 60000000
0x460864 4E800020 60000000
0x45f8c0 2F9F0008 2F9F0010
0x45f914 2F9F0008 2F9F0010
0x45fa70 2F9F0008 2F9F0010
0x45fc08 2F9F0008 2F9F0010
0x45fce8 2F9F0008 2F9F0010
0x45fe14 2F9F0008 2F9F0010
0x45fed8 2F9F0008 2F9F0010
0x45ff30 2F9F0008 2F9F0010
0x45ffb8 2F9F0008 2F9F0010
0x460040 2F9F0008 2F9F0010
0x4600a0 2F9F0008 2F9F0010
0x460100 2F9F0008 2F9F0010
0x460160 2F9F0008 2F9F0010
0x460704 2F9F0008 2F9F0010
0x46075c 2F9F0008 2F9F0010
0x460c60 2F9F0008 2F9F0010
0x45fe70 2F9E0001 2F9E0002
0x460230 2F9E0001 2F9E0002
0x4602b0 2F9E0001 2F9E0002
0x4608a0 2F9E0001 2F9E0002
0x460938 2F9E0001 2F9E0002
0x460648 2F9D0001 2F9D0002
EOF

MODE="${1:-verify}"
n=0; bad=0
while read -r addr orig new; do
    [ -z "$addr" ] && continue
    case "$MODE" in
      apply)  poke "$addr" "$new"; cur=$(rd "$addr"); [ "$cur" = "$new" ] || { echo "FEHLER $addr: $cur != $new"; bad=$((bad+1)); } ;;
      revert) poke "$addr" "$orig"; cur=$(rd "$addr"); [ "$cur" = "$orig" ] || { echo "FEHLER $addr: $cur != $orig"; bad=$((bad+1)); } ;;
      verify) cur=$(rd "$addr"); [ "$cur" = "$new" ] && echo "$addr gepatcht" || { [ "$cur" = "$orig" ] && echo "$addr original" || echo "$addr ??? $cur"; } ;;
    esac
    n=$((n+1))
done <<< "$TABLE"
echo "$MODE: $n Woerter, $bad Fehler"
