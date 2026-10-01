#!/bin/bash
# Upload the overlay files that differ between a packed PDIPFS and what the console has, and verify each one
# by reading it back and comparing the SHA1 - a size check is not enough: on 2026-09-22 and 2026-10-01 an
# ad-hoc script wrote the files to USRDIR/<path> instead of USRDIR/PDIPFS/<path>, the size check compared the
# misplaced file with itself and reported "ok", and the console kept running the old overlay for ten days.
#   Usage: PS3=<ip> push_overlay_ps3.sh <packed-pdipfs-dir> <file-list>   (file list = paths like 9/7T/X6)
PS3IP="${PS3:-192.168.1.6}"
BASE="ftp://$PS3IP/dev_hdd0/game/BCES00569/USRDIR/PDIPFS"
SRC="${1:?usage: push_overlay_ps3.sh <packed-pdipfs-dir> <file-list>}"
LIST="${2:?file list}"
TMP=$(mktemp -d)
curl -s --max-time 15 "http://$PS3IP/home.ps3mapi" | grep -q "_main_EBOOT.BIN" && { echo "GT5 is running - quit it first"; exit 2; }
ok=1
while read -r r; do
    f="$SRC/$r"
    for n in 1 2 3; do curl -s --max-time 300 --ftp-create-dirs -T "$f" "$BASE/$r" && break; sleep 2; done
    curl -s --max-time 300 "$BASE/$r" -o "$TMP/back" || { echo "  $r  read-back failed"; ok=0; continue; }
    a=$(sha1sum "$f" | cut -d' ' -f1); b=$(sha1sum "$TMP/back" | cut -d' ' -f1)
    if [ "$a" = "$b" ]; then printf '  %-12s %9s bytes  sha1 ok\n' "$r" "$(stat -c %s "$f")"
    else printf '  %-12s MISMATCH local %s console %s\n' "$r" "${a:0:12}" "${b:0:12}"; ok=0; fi
done < "$LIST"
rm -rf "$TMP"
[ $ok = 1 ] && echo "INSTALL OK (verified by hash)" || echo "INSTALL FAILED"
