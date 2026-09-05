#!/usr/bin/env python3
"""
GT5 2.17 EBOOT patch, phase 2 step 1: raise the number of *player* car slots
the engine allocates in split-screen from 2 to N (default 3).

Background
----------
The engine decides how many car slots to create in two twin functions:

  0x0037b208   r31 = hword[raceparam+0x18]
               mode = sbyte[raceparam+0x4b]        // 1 = single, 2/3 = split
               if (mode == 2 || mode == 3) r31 += 2;   <-- 0x37b250
               else if (mode == 1)         r31 += 1;
               r31 = clamp against 0x379bf0

  0x00379bf0   r9  = hword[raceparam+0x36]
               if (mode == 2 || mode == 3) r9 += 2;    <-- 0x379c30
               else if (mode == 1)         r9 += 1;
               return min(r9, hword[raceparam+0x1a])   // 0x1a = racers_max

The result is stored to Organizer+0x984 at 0x00390458 -- exactly the slot
count that getLoadedCarCount() / hasLoadingCarDone() iterate over. With the
hard-wired 2 the third player car never gets a slot, so the loading screen
waits forever.

This patch only changes the two immediates. The min() against racers_max
stays in place, so a normal 2-player split is still clamped to 2 and nothing
else in the game changes.

Usage:  python3 patch_eboot_p2.py EBOOT.elf EBOOT_patched.elf [players]
"""
import sys, hashlib

SEGS = [(0x0, 0x10000, 0x169e6e8), (0x16a0000, 0x16b0000, 0x11f9d8)]


def va2off(v):
    for fo, va, sz in SEGS:
        if va <= v < va + sz:
            return fo + (v - va)
    raise ValueError('address 0x%x not in a known segment' % v)


# va -> (instruction word with the old immediate, human readable)
SITES = [
    (0x0037b250, 0x3bff0002, 'addi r31, r31, 2  (slot count, 0x37b208)'),
    (0x00379c30, 0x39290002, 'addi r9, r9, 2    (slot cap,   0x379bf0)'),
]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    players = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    if not 2 <= players <= 8:
        sys.exit('players must be 2..8')

    d = bytearray(open(src, 'rb').read())
    print('input : %s  (%d bytes, sha1 %s)'
          % (src, len(d), hashlib.sha1(d).hexdigest()))

    for va, expect, desc in SITES:
        off = va2off(va)
        cur = int.from_bytes(d[off:off + 4], 'big')
        if cur == (expect & ~0xffff) | players:
            print('  0x%08x  already patched to %d' % (va, players))
            continue
        if cur != expect:
            sys.exit('  0x%08x  UNEXPECTED bytes %08x (expected %08x) -- '
                     'wrong EBOOT version?' % (va, cur, expect))
        new = (expect & ~0xffff) | players
        d[off:off + 4] = new.to_bytes(4, 'big')
        print('  0x%08x  %08x -> %08x   %s' % (va, expect, new, desc))

    open(dst, 'wb').write(d)
    print('output: %s  (sha1 %s)' % (dst, hashlib.sha1(d).hexdigest()))
    print('player car slots in split screen: %d' % players)


if __name__ == '__main__':
    main()
