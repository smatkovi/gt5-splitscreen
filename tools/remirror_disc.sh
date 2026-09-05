#!/bin/bash
# Re-fetch the disc files that the old two-connection mirror corrupted.
# Single FTP connection only - webMAN returns garbage when several connections
# read the same file in parallel.
set -u
PS3="${PS3:-192.168.1.11}"
D="$HOME/gt5re/disc/game"
V="$HOME/gt5re/tools/verify_remote.py"

fetch() {  # fetch <relative path>
    local rel="$1"
    local dir; dir="$(dirname "$D/$rel")"
    mkdir -p "$dir"
    echo "=== $rel ==="
    aria2c -x1 -s1 --continue=true --console-log-level=warn --summary-interval=0 \
           --allow-overwrite=false -d "$dir" -o "$(basename "$rel")" \
           "ftp://$PS3/dev_bdvd/$rel" || return 1
    python3 "$V" "$D/$rel" "/dev_bdvd/$rel" 8
}

for rel in "$@"; do
    fetch "$rel" || echo "FAILED: $rel"
done
echo "remirror done"
