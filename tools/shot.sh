#!/bin/bash
# Grab a screenshot of the RPCS3 game window (or the whole root window as fallback).
# Usage: shot.sh <output.png>
set -e
OUT="${1:?usage: shot.sh <out.png>}"
export DISPLAY="${DISPLAY:-:0}"
WID=""
for w in $(xdotool search --class rpcs3 2>/dev/null); do
    n=$(xdotool getwindowname "$w" 2>/dev/null || true)
    case "$n" in FPS:*) WID="$w" ;; esac
done
if [ -n "$WID" ]; then
    xdotool windowraise "$WID" 2>/dev/null; sleep 0.3
    import -window "$WID" "$OUT" 2>/dev/null || import -window root "$OUT"
else
    import -window root "$OUT"
fi
echo "$OUT ${WID:-root}"
