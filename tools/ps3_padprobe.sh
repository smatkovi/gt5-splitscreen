#!/bin/bash
# Read-only probe of GT5's pad manager on the PS3 (global object at 0x18ef8f8, same layout as in
# RPCS3): per-port connection status, port setting, capability and the last CellPadData for
# ports 0..3.  Run while a race is on and someone presses buttons on the pad under test.
#   Usage: PS3=192.168.1.11 ps3_padprobe.sh [rounds=5]
: "${PS3:?set PS3=<console ip>}"
ROUNDS="${1:-5}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] || { echo "no game process"; exit 1; }
rd() { curl -s --max-time 25 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=$2" | grep -oiE '\b([0-9A-F]{2} ){3}[0-9A-F]{2}\b' | tr -d ' \n'; }
PM=0x018EF8F8
words() { local h="$1"; local i; for ((i=0; i<${#h}; i+=8)); do printf '%s ' "${h:i:8}"; done; echo; }
echo "pid=$PID  pad manager @$PM"
echo "hdr(+0x00): $(words "$(rd $PM 12)")   (max ports, now_connect, ?)"
echo "connected(+0x0c): $(words "$(rd 0x018EF904 28)")"
echo "setting  (+0x28): $(words "$(rd 0x018EF920 28)")"
echo "capabil. (+0x44): $(words "$(rd 0x018EF93C 28)")"
for r in $(seq 1 "$ROUNDS"); do
    for p in 0 1 2 3; do
        A=$(printf '0x%08X' $((0x018EF8F8 + 0xa0 + p*0x84)))
        H=$(rd $A 24)
        [ -z "$H" ] && { echo "port $p: <read failed>"; continue; }
        len=$((16#${H:0:8})); b1=${H:12:4}; d1=${H:16:4}; d2=${H:20:4}
        printf 'round %d port %d: len=%-3d button[1]=%s digital1=%s digital2=%s sticks=%s %s %s %s\n' $r $p $len $b1 $d1 $d2 ${H:24:4} ${H:28:4} ${H:32:4} ${H:36:4}
    done
    # per-player objects (deterministic heap addresses, identical in RPCS3 and on the console):
    # +0x34 = player index, +0x0c..+0x18 input state bits, +0x3198/+0x31a4 index, +0x31a8 race entry
    for i in 0 1 2; do
        case $i in 0) O=0x4FA78000;; 1) O=0x4FA6C000;; 2) O=0x4FA48000;; esac
        H=$(rd $O 64); F=$(rd $(printf '0x%08X' $((O + 0xa0))) 12)
        # +0xa4 flipped 0 -> 1 in RPCS3 while pad 2 held cross (in player 2 AND player 0 objects, not with pad 0) -
        # ambiguous, treat as a hint only; the pad-manager rows above are the primary evidence
        [ -n "$H" ] && echo "player $i obj $O: accel-flag(+0xa4)=${F:8:8} hdr: $(words "$H")" || echo "player $i obj $O: <read failed>"
    done
    sleep 2
done
