#!/bin/bash
# Upload a release folder (release/3p or release/4p) to the PS3 over webMAN FTP:
#   - EBOOT.BIN -> /dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN   (the console keeps EBOOT.BIN.orig)
#   - mod/pdipfs/**  -> /dev_hdd0/game/BCES00569/USRDIR/PDIPFS/<same relative path>
# then re-lists every uploaded file and compares the size.  Refuses to run while GT5 is running
# (the EBOOT is in use); quit the game first.  Usage: PS3=192.168.1.11 deploy_ps3_release.sh release/3p
set -e
: "${PS3:?set PS3=<console ip>}"
REL="${1:?usage: deploy_ps3_release.sh <release dir>}"
BASE="ftp://$PS3/dev_hdd0/game/BCES00569/USRDIR"
[ -f "$REL/EBOOT.BIN" ] && [ -d "$REL/mod/pdipfs" ] || { echo "not a release folder: $REL" >&2; exit 1; }
if curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -qiE 'proc=0x[0-9a-f]+'; then
    echo "a game process is running on the PS3 - quit GT5 first (XMB), then rerun." >&2; exit 2
fi
curl -s --max-time 15 "$BASE/" | grep -q 'EBOOT.BIN.orig' || { echo "no EBOOT.BIN.orig backup on the console - refusing" >&2; exit 3; }
up() {  # up <local> <remote-path-below-USRDIR>
    local f="$1" r="$2" n=0
    while :; do
        curl -s --max-time 300 --ftp-create-dirs -T "$f" "$BASE/$r" && break
        n=$((n+1)); [ $n -ge 3 ] && { echo "upload failed: $r" >&2; exit 4; }; sleep 2
    done
    local want have; want=$(stat -c %s "$f")
    have=$(curl -s --max-time 15 "$BASE/$(dirname "$r")/" | awk -v b="$(basename "$r")" '$NF==b {print $5}')
    printf '  %-28s %9s bytes  %s\n' "$r" "$want" "$([ "$want" = "$have" ] && echo ok || echo "SIZE MISMATCH (console has $have)")"
    [ "$want" = "$have" ]
}
echo "uploading $REL to $PS3 ..."
up "$REL/EBOOT.BIN" "EBOOT.BIN"
find "$REL/mod/pdipfs" -type f | while read -r f; do up "$f" "PDIPFS/${f#$REL/mod/pdipfs/}"; done
echo "done. Start GT5 from the XMB; 'deploy_*.sh verify' should then report patched=288."
