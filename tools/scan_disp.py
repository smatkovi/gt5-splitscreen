#!/usr/bin/env python3
"""Scan the decrypted EBOOT for D-form accesses with a given displacement.

Used to find every reader/writer of WindowManager fields (+0x2c window_max,
+0x30 clamp) that the three-window patch has to relocate.

Usage: scan_disp.py <start-va> <end-va> <disp> [<disp> ...]
"""
import struct
import sys

SEGS = [(0x0, 0x10000, 0x169e6e8), (0x16a0000, 0x16b0000, 0x11f9d8)]
D = open('/home/sebastian/gt5re/EBOOT.elf', 'rb').read()

# D-form load/store opcodes we care about
OPS = {32: 'lwz', 33: 'lwzu', 36: 'stw', 37: 'stwu',
       34: 'lbz', 35: 'lbzu', 38: 'stb', 39: 'stbu',
       40: 'lhz', 41: 'lhzu', 42: 'lha', 44: 'sth',
       14: 'addi', 12: 'addic', 58: 'ld/lwa', 62: 'std/stdu'}


def va2off(v):
    for fo, va, sz in SEGS:
        if va <= v < va + sz:
            return fo + (v - va)
    return None


def main():
    start = int(sys.argv[1], 16)
    end = int(sys.argv[2], 16)
    disps = {int(a, 16) for a in sys.argv[3:]}
    o = va2off(start)
    n = (end - start) // 4
    words = struct.unpack('>%dI' % n, D[o:o + n * 4])
    for i, w in enumerate(words):
        op = w >> 26
        if op not in OPS:
            continue
        d = w & 0xffff
        if op in (58, 62):
            d &= 0xfffc          # DS-form: low two bits are the sub-opcode
        if d not in disps:
            continue
        va = start + i * 4
        rt = (w >> 21) & 31
        ra = (w >> 16) & 31
        print(f'{va:08x}  {w:08X}  {OPS[op]:6s} r{rt}, 0x{d:x}(r{ra})')


if __name__ == '__main__':
    main()
