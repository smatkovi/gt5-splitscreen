#!/usr/bin/env python3
"""Tiny PowerPC encoder for the handful of instruction forms the GT5 patches need, plus a
capstone round-trip check.  Import from patch generators; never hand-encode words."""
from capstone import Cs, CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN

_md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)


def _d(op, rt, ra, imm):
    assert -0x8000 <= imm <= 0xffff
    return (op << 26) | (rt << 21) | (ra << 16) | (imm & 0xffff)


def lwz(rt, d, ra):   return _d(32, rt, ra, d)
def stw(rs, d, ra):   return _d(36, rs, ra, d)
def lbz(rt, d, ra):   return _d(34, rt, ra, d)
def stb(rs, d, ra):   return _d(38, rs, ra, d)
def addi(rt, ra, imm): return _d(14, rt, ra, imm)
def li(rt, imm):      return addi(rt, 0, imm)
def lis(rt, imm):     return _d(15, rt, 0, imm)
def ori(ra, rs, imm): return (24 << 26) | (rs << 21) | (ra << 16) | (imm & 0xffff)
def cmpwi(crf, ra, imm): return (11 << 26) | (crf << 23) | (ra << 16) | (imm & 0xffff)
def cmpw(crf, ra, rb):   return (31 << 26) | (crf << 23) | (ra << 16) | (rb << 11) | (0 << 1)
def add(rt, ra, rb):  return (31 << 26) | (rt << 21) | (ra << 16) | (rb << 11) | (266 << 1)
def mr(rt, rs):       return (31 << 26) | (rs << 21) | (rt << 16) | (rs << 11) | (444 << 1)  # or rt,rs,rs
def nop():            return 0x60000000


def b(pc, target, link=False):
    off = target - pc
    assert -0x2000000 <= off < 0x2000000 and off % 4 == 0, hex(off)
    return (18 << 26) | (off & 0x03fffffc) | (1 if link else 0)


def bl(pc, target): return b(pc, target, True)


def bc(pc, bo, bi, target):
    off = target - pc
    assert -0x8000 <= off < 0x8000 and off % 4 == 0
    return (16 << 26) | (bo << 21) | (bi << 16) | (off & 0xfffc)


def bne(pc, target, crf=7): return bc(pc, 4, crf * 4 + 2, target)
def beq(pc, target, crf=7): return bc(pc, 12, crf * 4 + 2, target)
def blt(pc, target, crf=7): return bc(pc, 12, crf * 4 + 0, target)


def cmplwi(crf, ra, imm):
    assert 0 <= imm <= 0xffff
    return (10 << 26) | (crf << 23) | (ra << 16) | imm


def rlwinm(ra, rs, sh, mb, me):
    return (21 << 26) | (rs << 21) | (ra << 16) | (sh << 11) | (mb << 6) | (me << 1)


def slwi(ra, rs, n): return rlwinm(ra, rs, n, 0, 31 - n)


def bgt(pc, target, crf=7): return bc(pc, 12, crf * 4 + 1, target)


def blr(): return 0x4e800020


def dis(addr, word):
    ins = list(_md.disasm(word.to_bytes(4, 'big'), addr))
    return f'{ins[0].mnemonic} {ins[0].op_str}' if ins else '???'


def show(words):
    for a, w in words:
        print(f'{a:08x} {w:08X}  {dis(a, w)}')
