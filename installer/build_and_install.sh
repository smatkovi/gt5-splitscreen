#!/bin/bash
# One command: fetch your own EBOOT off the console, build the installer package from it,
# and put that package back on the console ready to install.
#
#   PS3=192.168.0.2 ./build_and_install.sh [3p|4p]
#
# Nothing about the game travels anywhere else - the EBOOT is read from your console and the
# package built from it goes straight back to the same console.
#
# Requirements: a PS3 with CFW/HEN running webMAN (FTP on port 21), GT5 with update 2.17
# installed, $PSL1GHT pointing at a ps3dev toolchain, and scetool with a keys file (SCETOOL=).
#
# Note: webMAN returns corrupt data when several FTP connections read the same file at once,
# so every transfer here uses a single connection and is size-checked afterwards.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VARIANT="${1:-4p}"
: "${PS3:?set PS3=<console ip>, e.g. PS3=192.168.0.2 $0 $VARIANT}"
case "$VARIANT" in 3p|4p) ;; *) echo "variant must be 3p or 4p" >&2; exit 1;; esac

GAME="ftp://$PS3/dev_hdd0/game/BCES00569/USRDIR"
WORK="$HERE/build/$VARIANT"
ORIG_MD5="a8924d1fdca785acab26ee7854bd650a"
ORIG_SIZE=9505120

step() { printf '\n== %s ==\n' "$*"; }
say()  { printf '  %s\n' "$*"; }

step "console $PS3"
curl -s --max-time 15 "$GAME/" >/dev/null 2>&1 || {
    echo "cannot reach $GAME" >&2
    echo "Is the console on, webMAN running and the FTP server reachable? Try http://$PS3/" >&2
    exit 2; }
say "reachable"

# A running game holds EBOOT.BIN open; webMAN's PS3MAPI reports the active process.
if curl -s --max-time 10 "http://$PS3/home.ps3mapi" 2>/dev/null | grep -qiE 'proc=0x[0-9a-f]+'; then
    echo "A game is running on the console. Quit it from the XMB first." >&2
    exit 3
fi

step "fetching your EBOOT"
mkdir -p "$WORK"
fetch() {  # fetch <remote name> <local file>; single connection, size checked
    local name="$1" out="$2" want
    want=$(curl -s --max-time 40 "$GAME/" | awk -v b="$name" '$NF==b {print $5}' | head -1)
    [ -n "$want" ] || return 1
    curl -s --max-time 600 -o "$out" "$GAME/$name" || return 1
    [ "$(stat -c %s "$out")" = "$want" ] || {
        echo "short read: $name is $want bytes on the console, got $(stat -c %s "$out")" >&2
        return 1; }
    return 0
}

SRC="$WORK/EBOOT_from_console.BIN"
fetch "EBOOT.BIN" "$SRC" || { echo "could not download EBOOT.BIN" >&2; exit 4; }
got=$(md5sum "$SRC" | cut -d' ' -f1)
say "EBOOT.BIN  $(stat -c %s "$SRC") bytes  md5 $got"

if [ "$got" != "$ORIG_MD5" ]; then
    say "not the untouched 2.17 EBOOT - looking for the installer's backup"
    if fetch "EBOOT.BIN.orig" "$SRC" && [ "$(md5sum "$SRC" | cut -d' ' -f1)" = "$ORIG_MD5" ]; then
        say "using EBOOT.BIN.orig (the game is already patched)"
    else
        cat >&2 <<EOF

The EBOOT on the console is not the unmodified Gran Turismo 5 2.17 update, and there
is no usable EBOOT.BIN.orig backup next to it.
  expected md5 $ORIG_MD5  ($ORIG_SIZE bytes)
  found        $got

Install / reinstall update 2.17 on the console, then run this again.
EOF
        exit 5
    fi
fi

step "building the package"
"$HERE/build_pkg.sh" "$SRC" "$VARIANT"
PKG="$HERE/gt5-$VARIANT-installer.pkg"
[ -f "$PKG" ] || { echo "no package produced" >&2; exit 6; }

step "uploading to the console"
REMOTE="ftp://$PS3/dev_hdd0/packages/$(basename "$PKG")"
n=0
until curl -s --max-time 600 --ftp-create-dirs -T "$PKG" "$REMOTE"; do
    n=$((n+1)); [ $n -ge 3 ] && { echo "upload failed" >&2; exit 7; }; sleep 2
done
want=$(stat -c %s "$PKG")
have=$(curl -s --max-time 40 "ftp://$PS3/dev_hdd0/packages/" \
       | awk -v b="$(basename "$PKG")" '$NF==b {print $5}' | head -1)
[ "$want" = "$have" ] || { echo "size mismatch after upload: sent $want, console has ${have:-nothing}" >&2; exit 8; }
say "$(basename "$PKG")  $want bytes  ok"

cat <<EOF

Done. On the console:
  1. XMB -> Install Package Files -> $(basename "$PKG")
  2. run "GT5 ${VARIANT^^} Split Screen Installer" from the XMB and confirm
  3. start Gran Turismo 5: Arcade -> 2P Split Screen -> track -> cars,
     then answer the extra player prompts with yes

The installer keeps EBOOT.BIN.orig on the console; running it again restores it.
EOF
