#!/bin/bash
# Build a personal GT5 3P/4P split-screen installer package.
#
#   ./build_pkg.sh <your EBOOT.BIN> [3p|4p]
#
# <your EBOOT.BIN> is the EBOOT of YOUR OWN copy of the Gran Turismo 5 2.17 update,
# copied off your console from
#   /dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN
#
# No part of the game is distributed with this repository. This script decrypts your
# EBOOT, applies the patch word list from release/<variant>/words.txt, re-encrypts it,
# and wraps the result together with the script overlay into an installable .pkg.
#
# Requirements:
#   - a ps3dev/PSL1GHT toolchain in $PSL1GHT (ppu-gcc, make_self_npdrm, pkg.py, sfo.py,
#     package_finalize, sprxlinker)
#   - scetool with a keys file, for decrypting and re-encrypting the EBOOT.
#     Point SCETOOL at the binary; it expects its keys in <scetool dir>/data/keys.
#     Neither the tool nor the keys are part of this repository.
#   - python3
set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"
IN_EBOOT="${1:?usage: build_pkg.sh <your EBOOT.BIN> [3p|4p]}"
VARIANT="${2:-4p}"
SCETOOL="${SCETOOL:-$BASE/eboot/scetool/scetool}"
PYTHON="${PYTHON:-python3}"

case "$VARIANT" in 3p|4p) ;; *) echo "variant must be 3p or 4p" >&2; exit 1;; esac

REL="$BASE/release/$VARIANT"
WORK="$BASE/installer/build/$VARIANT"
PKGDIR="$WORK/pkg"

# md5 of the untouched EBOOT.BIN of the 2.17 update, sha1 of its decrypted form
ORIG_MD5="a8924d1fdca785acab26ee7854bd650a"
ORIG_ELF_SHA1="306f86c62b9f03041c903be96ac59e5c3f130452"

say() { printf '  %s\n' "$*"; }

[ -f "$IN_EBOOT" ] || { echo "not found: $IN_EBOOT" >&2; exit 1; }
IN_EBOOT="$(realpath "$IN_EBOOT")"   # scetool runs from its own directory
[ -d "$REL" ] || { echo "no release folder: $REL" >&2; exit 1; }
[ -f "$REL/words.txt" ] || { echo "no patch word list: $REL/words.txt" >&2; exit 1; }
: "${PSL1GHT:?set PSL1GHT to your ps3dev installation}"

echo "== checking your EBOOT =="
got_md5=$(md5sum "$IN_EBOOT" | cut -d' ' -f1)
say "md5 $got_md5"
if [ "$got_md5" != "$ORIG_MD5" ]; then
    cat >&2 <<EOF

This is not the EBOOT.BIN of the Gran Turismo 5 2.17 update.
  expected md5 $ORIG_MD5  (BCES00569, update 2.17, 9505120 bytes)
  got          $got_md5

Install update 2.17 on your console, then copy
/dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN off it again. If your EBOOT is already
patched, use the backup EBOOT.BIN.orig that the installer left next to it.
EOF
    exit 2
fi

echo "== decrypting =="
[ -x "$SCETOOL" ] || { echo "scetool not found or not executable: $SCETOOL (set SCETOOL=)" >&2; exit 3; }
mkdir -p "$WORK"
( cd "$(dirname "$SCETOOL")" && ./"$(basename "$SCETOOL")" -d "$IN_EBOOT" "$WORK/EBOOT_orig.elf" ) >/dev/null
got_sha1=$(sha1sum "$WORK/EBOOT_orig.elf" | cut -d' ' -f1)
say "decrypted sha1 $got_sha1"
[ "$got_sha1" = "$ORIG_ELF_SHA1" ] || {
    echo "decrypted ELF does not match the expected 2.17 executable ($ORIG_ELF_SHA1)" >&2; exit 4; }

echo "== applying $(grep -cvE '^\s*(#|$)' "$REL/words.txt") patch words =="
"$PYTHON" - "$WORK/EBOOT_orig.elf" "$WORK/EBOOT_patched.elf" "$REL/words.txt" <<'PY'
import struct, sys, pathlib
src, dst, words = sys.argv[1], sys.argv[2], sys.argv[3]
data = bytearray(pathlib.Path(src).read_bytes())
n = 0
for line in open(words):
    p = line.split()
    if len(p) < 3 or line.lstrip().startswith('#'):
        continue
    try:
        addr, old, new = int(p[0], 16), int(p[1], 16), int(p[2], 16)
    except ValueError:
        continue
    off = addr - 0x10000
    cur = struct.unpack('>I', data[off:off+4])[0]
    if cur != old:
        raise SystemExit(f'{addr:#x}: found {cur:08X}, expected {old:08X} - wrong executable')
    data[off:off+4] = struct.pack('>I', new)
    n += 1
pathlib.Path(dst).write_bytes(data)
print(f'  {n} words applied')
PY

echo "== re-encrypting =="
SC_DIR="$(dirname "$SCETOOL")"
( cd "$SC_DIR" && ./"$(basename "$SCETOOL")" -0 SELF -1 TRUE -s FALSE -2 19 \
    -3 1010000001000003 -4 01000002 -5 NPDRM -A 0001000000000000 -6 0004001000000000 \
    -b FREE -c UEXEC -f EP9001-BCES00569_00-0000000000000000 -g EBOOT.BIN \
    -t "$IN_EBOOT" -e "$WORK/EBOOT_patched.elf" "$WORK/EBOOT_patched.BIN" ) \
  2>&1 | grep -E 'written|Error' || true
[ -s "$WORK/EBOOT_patched.BIN" ] || { echo "re-encryption produced no output" >&2; exit 5; }
if [ -f "$BASE/tools/npdrm_fixup.py" ]; then
    "$PYTHON" "$BASE/tools/npdrm_fixup.py" "$WORK/EBOOT_patched.BIN"
fi
say "$(stat -c %s "$WORK/EBOOT_patched.BIN") bytes"

echo "== staging payload =="
rm -rf "$PKGDIR/USRDIR/payload"
mkdir -p "$PKGDIR/USRDIR/payload"
cp "$WORK/EBOOT_patched.BIN" "$PKGDIR/USRDIR/payload/EBOOT.BIN"
if [ -d "$REL/mod/pdipfs" ]; then
    cp -r "$REL/mod/pdipfs" "$PKGDIR/USRDIR/payload/pdipfs"
    say "$(find "$PKGDIR/USRDIR/payload/pdipfs" -type f | wc -l) PDIPFS file(s)"
else
    cat >&2 <<EOF

No script overlay at $REL/mod/pdipfs.

The EBOOT patch alone is not enough - the extra players are set up by the Adhoc
script mod. Build it once with

    MOD_WINDOW_MAX=${VARIANT%p} tools/build_mod.sh mod_x

(needs .NET, GTAdhocToolchain, GTToolsSharp and an OpenAdhoc checkout; see
tools/build_mod.sh), then copy the resulting pdipfs overlay to $REL/mod/pdipfs.
EOF
    exit 6
fi

echo "== building package =="
# make only tracks the installer binary, not the staged payload, so a rebuild with a
# fresh payload would otherwise be skipped as up to date.
rm -f "$BASE/installer/gt5-$VARIANT-installer.pkg"
make -C "$BASE/installer" VARIANT="$VARIANT" pkg

OUT="$BASE/installer/gt5-$VARIANT-installer.pkg"
echo
echo "done: $OUT"
echo "Copy it to /dev_hdd0/packages/ on your console and install it from the"
echo "package manager, then run \"GT5 ${VARIANT^^} Split Screen Installer\" from the XMB."
