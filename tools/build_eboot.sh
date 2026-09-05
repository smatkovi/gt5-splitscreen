#!/bin/bash
# Build a patched, re-encrypted GT5 2.17 EBOOT.BIN (NPDRM UEXEC, key revision 0x19, licence FREE,
# unsigned = "fake signed", accepted by CFW like any homebrew SELF) from the decrypted EBOOT.elf
# and word lists.  Usage: build_eboot.sh <out.BIN> <words.txt> [...]
set -e
OUT="${1:?usage: build_eboot.sh <out.BIN> <words.txt>...}"; shift
BASE="$HOME/gt5re"; SC="$BASE/eboot/scetool"
mkdir -p "$SC/data"; cp "$BASE/tools/scetool_keys.txt" "$SC/data/keys"
ELF="${OUT%.BIN}.elf"
"$BASE/.venv/bin/python" - "$BASE/EBOOT.elf" "$ELF" "$@" <<'PY'
import struct, sys, pathlib
src, dst, files = sys.argv[1], sys.argv[2], sys.argv[3:]
data = bytearray(pathlib.Path(src).read_bytes()); n = 0
for f in files:
    for line in open(f):
        p = line.split()
        if len(p) != 3: continue
        a, o, w = int(p[0], 16), int(p[1], 16), int(p[2], 16)
        off = a - 0x10000
        cur = struct.unpack('>I', data[off:off+4])[0]
        assert cur == o, f'{f}: {a:#x} has {cur:08X}, expected {o:08X}'
        data[off:off+4] = struct.pack('>I', w); n += 1
pathlib.Path(dst).write_bytes(data); print(dst, n, 'words applied')
PY
(cd "$SC" && ./scetool -0 SELF -1 TRUE -s FALSE -2 19 -3 1010000001000003 -4 01000002 -5 NPDRM -A 0001000000000000 -6 0004001000000000 \
   -b FREE -c UEXEC -f EP9001-BCES00569_00-0000000000000000 -g EBOOT.BIN -t "$BASE/update/USRDIR/EBOOT.BIN" -e "$ELF" "$OUT" 2>&1 | grep -E 'written|Error') 
(cd "$SC" && ./scetool -d "$OUT" "$OUT.rt.elf" >/dev/null 2>&1) && cmp "$OUT.rt.elf" "$ELF" && rm -f "$OUT.rt.elf" && echo "round trip OK: $OUT"
