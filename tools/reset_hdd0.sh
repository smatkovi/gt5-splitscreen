#!/bin/bash
# Restore the RPCS3 copy of the GT5 game folder to the pristine console state.
# GT5 writes into PDIPFS (files copied from GT.VOL on demand, *.psctmp, PDIPFS_bdmark) - after
# a run against a corrupt GT.VOL those cached files are suspect, so mirror the master with --delete
# (the PKG-installed files are a subset of the master, verified 2026-09-05).
# Also clears /dev_hdd1 (GT5 page files).
set -e
SRC="$HOME/gt5re/update"
DST="$HOME/.config/rpcs3/dev_hdd0/game/BCES00569"
pgrep -x rpcs3 >/dev/null && { echo "stop rpcs3 first" >&2; exit 1; }
rsync -a --delete --exclude 'PDIPFS_extracted' --exclude 'EBOOT.elf' "$SRC/" "$DST/"
rm -rf "$HOME/.config/rpcs3/dev_hdd1"/*
echo "hdd0 game folder reset: $(du -sh "$DST" | cut -f1)"
