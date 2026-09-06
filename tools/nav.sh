#!/bin/bash
# Image-driven navigation of GT5 in RPCS3 from the startup dialogs to a loaded split-battle race.
# States are recognised by comparing fixed crops of a fresh screenshot with reference crops in
# tools/nav_ref (ImageMagick compare, normalised RMSE). Every screenshot is kept in $OUT.
#   Usage: nav.sh [players=3] [outdir]
export DISPLAY="${DISPLAY:-:0}"
PLAYERS="${1:-3}"
OUT="${2:-/tmp/claude-1000/-home-sebastian-gt5re/dbf528eb-341b-4af6-a61d-a4e3f03a32da/scratchpad/nav}"
T="$HOME/gt5re/tools"; R="$T/nav_ref"
mkdir -p "$OUT"
classify() { "$HOME/gt5re/.venv/bin/python" "$T/classify.py" "$1"; }
match() { [ "$(classify "$1")" = "$2" ]; }
press() { "$T/pad.sh" "$@" >/dev/null; }
n=0; car_step=0; round=1; dialogs=0; last=""; same=0; seen_menu=0; t0=$(date +%s)
while :; do
    n=$((n+1)); shot="$OUT/$(printf %03d $n).png"
    "$T/shot.sh" "$shot" >/dev/null
    st=$(classify "$shot")
    if [ "$st" = "$last" ]; then same=$((same+1)); else same=0; fi
    last="$st"
    echo "$(date +%H:%M:%S) #$n $st"
    if grep -q 'Access violation\|Emulation has been frozen' "$HOME/.cache/rpcs3/RPCS3.log"; then echo "CRASH detected"; exit 2; fi
    case "$st" in
        install)  press Left; press X; sleep 8 ;;
        language) press X; sleep 8 ;;
        adjust)   press X; sleep 10 ;;
        psn)      seen_menu=1; press Left; press X; sleep 4 ;;
        nosignin) press X; sleep 4 ;;
        demo)     press X; sleep 5 ;;
        menubar|menubar2) seen_menu=1; press Right; sleep 1; press X; sleep 10 ;;
        arcade)   # MODE=single -> first arcade item (Single Race, 1 player); default: 2P Split Screen
                  if [ "${MODE:-split}" = single ]; then press X; else press Right Right Right; sleep 1; press X; fi; sleep 8 ;;
        track)    press X; sleep 8 ;;
        car)      # round 1: players 1/2 pick the default car; round 2 (after the player dialogs) again for players 3/4
                  # (MODE=single: the same X presses walk through the 1P car select)
                  # (both rounds are operated by pads 1/2; in round 2 they pick for players 3/4)
                  case $car_step in
                    0) press X; sleep 4 ;;
                    1) press n; sleep 5 ;;
                    2) press X; sleep 2; press n; sleep 6 ;;
                    *) sleep 4 ;;
                  esac; car_step=$((car_step+1)) ;;
        options)  press X; sleep 2; press n; sleep 6 ;;
        okdialog) press X; sleep 5 ;;
        p3dialog|p4dialog)
                  # the player dialogs now follow car-select round 1; a third dialog announces round 2
                  if [ $dialogs -eq 0 ] && [ "$PLAYERS" -lt 3 ]; then press Left; fi
                  if [ $dialogs -eq 1 ] && [ "$PLAYERS" -lt 4 ]; then press Left; fi
                  press X; sleep 5; dialogs=$((dialogs+1))
                  if [ "$PLAYERS" -ge 3 ]; then round=2; car_step=0; fi ;;
        badshot)  W=$(xdotool search --name "^FPS:" | head -1); xdotool windowmove "$W" 0 0 2>/dev/null; sleep 4 ;;
        loading)  echo "LOADING reached after $(( $(date +%s)-t0 ))s"; exit 0 ;;
        unknown)  # intro video: Start skips it. Never press Start once the menu was seen (it toggles the menu bar).
                  if [ $seen_menu = 0 ] && [ $same -ge 3 ]; then press Return; fi; sleep 6 ;;
    esac
    if [ $(( $(date +%s)-t0 )) -gt 900 ]; then echo "TIMEOUT"; exit 3; fi
done
