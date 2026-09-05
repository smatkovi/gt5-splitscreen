#!/usr/bin/env python3
"""Spot-check a locally mirrored file against the copy on the PS3 (webMAN FTP).

The console's FTP server honours REST offsets correctly, but it corrupts data when
several connections read the SAME file in parallel. Mirrors made with lftp pget or
`aria2c -x2` are therefore silently wrong in the middle. This tool finds that.

Usage: verify_remote.py <local-path> <remote-ftp-path> [chunks]
Example:
  verify_remote.py ~/gt5re/disc/game/PS3_GAME/USRDIR/GT.VOL /dev_bdvd/PS3_GAME/USRDIR/GT.VOL
"""
import hashlib
import os
import subprocess
import sys

HOST = os.environ.get('PS3', '192.168.1.11')
CHUNK = 65536


def remote_range(remote, start, length):
    return subprocess.run(
        ['curl', '-sS', '-m', '180', '--user', 'anonymous:',
         '-r', f'{start}-{start + length - 1}', f'ftp://{HOST}{remote}'],
        capture_output=True).stdout


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    local = os.path.expanduser(sys.argv[1])
    remote = sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 12

    size = os.path.getsize(local)
    print(f'{local}\n  size {size}')
    offsets = [0] + [size * i // n for i in range(1, n)] + [max(0, size - CHUNK)]
    bad = 0
    with open(local, 'rb') as fh:
        for start in offsets:
            length = min(CHUNK, size - start)
            r = remote_range(remote, start, length)
            fh.seek(start)
            l = fh.read(length)
            ok = len(r) == len(l) and hashlib.md5(r).digest() == hashlib.md5(l).digest()
            if not ok:
                bad += 1
                first = next((k for k in range(min(len(r), len(l))) if r[k] != l[k]), None)
                extra = f' first differing byte at 0x{start + first:x}' if first is not None else ''
                print(f'  MISMATCH @0x{start:x} (remote {len(r)} B, local {len(l)} B){extra}')
            else:
                print(f'  ok       @0x{start:x}')
    print(f'--- {bad} of {len(offsets)} chunks bad ---')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
