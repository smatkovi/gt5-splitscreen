#!/usr/bin/env python3
"""Generate the 'window slots x4' patch: the WindowManager (inline in MOrganizer at +0xa90) keeps its
layout, but the window array moves to an external 4-slot array whose pointer lives in the dead
inline entry area at MOrganizer+0x2c0 (= WM-0x7d0).  Every in-place edit is asserted against the
original word and disassembled with capstone.  Output: win4_words.txt (addr orig new)."""
import struct, sys
sys.path.insert(0, '/home/sebastian/gt5re/tools')
from ppcasm import *

D = open('/home/sebastian/gt5re/EBOOT.elf', 'rb').read()
def W(a): return struct.unpack('>I', D[a - 0x10000:a - 0x10000 + 4])[0]

EXT = -0x7d0            # WM-relative offset of the external slot-array pointer (MOrg+0x2c0)
NWIN = 4
ALLOC = 0xbc1974
WIN_CTOR = 0x469320
NODE = 0x19472f0
CAVE = 0x1581000

out = {}   # addr -> new word
def put(a, new, expect=None):
    o = W(a)
    if expect is not None:
        assert o == expect, f'{a:#x}: orig {o:08X} != expected {expect:08X}'
    assert a not in out, f'double patch at {a:#x}'
    out[a] = new

# --- P1: index accessors  slwi rX,rX,3 ... addi rX,rX,0x10 ... add rD,r3,rX ... lwz rT,0xc(rD)
P1 = [0x45f2a8, 0x45f2c0, 0x45f340, 0x45f7ec, 0x45f9f8, 0x45fa9c, 0x45fb90, 0x45fd20, 0x45fd68, 0x45fdb0,
      0x4602d4, 0x460308, 0x460394, 0x4603ec, 0x460420, 0x46046c, 0x4604a4, 0x4604e0, 0x460544,
      0x460780, 0x4607cc, 0x460cc0]
def regs_written(w):
    op = w >> 26
    if op in (14, 15, 32, 34, 40, 42, 58, 24, 21):   # addi/lis/lwz/lbz/lhz/lha/ld/ori/rlwinm
        return {(w >> 21) & 31} if op not in (24, 21) else {(w >> 16) & 31}
    if op == 31:
        return {(w >> 21) & 31}
    return set()
for s in P1:
    w0 = W(s); assert (w0 >> 26) == 21 and ((w0 >> 11) & 31) == 3, hex(s)
    X = (w0 >> 16) & 31
    addi_a = add_a = lwz_a = None; D_ = A_ = None
    used = set()
    for k in range(1, 30):
        a = s + 4 * k; w = W(a)
        if addi_a is None and w == addi(X, X, 0x10):
            addi_a = a; continue
        if addi_a and add_a is None and (w >> 26) == 31 and ((w >> 1) & 0x3ff) == 266 and ((w >> 11) & 31) == X:
            add_a = a; D_ = (w >> 21) & 31; A_ = (w >> 16) & 31; continue
        if add_a and lwz_a is None and (w >> 26) == 32 and ((w >> 16) & 31) == D_ and (w & 0xffff) == 0xc:
            lwz_a = a; T = (w >> 21) & 31; break
        if add_a is None:
            used |= regs_written(w)
    assert addi_a and add_a and lwz_a, f'P1 pattern incomplete at {s:#x}: {addi_a} {add_a} {lwz_a}'
    S = 11 if 11 not in used else (10 if 10 not in used else None)
    assert S is not None, f'no scratch reg at {s:#x}'
    put(addi_a, lwz(S, EXT, A_))        # ext base of the WM whose window is indexed
    put(add_a, add(D_, S, X))
    put(lwz_a, lwz(T, 0, D_))
    print(f'P1 {s:#x}: base r{A_} idx r{X} -> r{D_}, load r{T} @ {lwz_a:#x} (scratch r{S})')

# --- P2: byte-offset loops  add r9,r30,r31 ; clrldi r9,r9,0x20 ; lwz rT,0x1c(r9) ; ... cmpwi cr7,r31,8
P2 = [0x45f8b8, 0x45f90c, 0x45fa68, 0x45fc00, 0x45fce0, 0x45fe0c, 0x45fed0, 0x45ff28, 0x45ffb0, 0x460038,
      0x460098, 0x4600f8, 0x460158, 0x4606fc, 0x460754, 0x460c44]
for s in P2:
    w = W(s); assert (w >> 26) == 32 and ((w >> 16) & 31) == 9 and (w & 0xffff) == 0x1c, hex(s)
    T = (w >> 21) & 31
    add_a = clr_a = None; B_ = None
    for k in range(1, 9):
        a = s - 4 * k; ww = W(a)
        if ww == 0x79290020 and clr_a is None: clr_a = a; continue
        # add r9, rB, r31
        if (ww >> 26) == 31 and ((ww >> 1) & 0x3ff) == 266 and ((ww >> 21) & 31) == 9 and 31 in ((ww >> 11) & 31, (ww >> 16) & 31) and add_a is None:
            add_a = a; B_ = ((ww >> 16) & 31) if ((ww >> 11) & 31) == 31 else ((ww >> 11) & 31); break
    assert add_a and clr_a and add_a < clr_a, f'P2 pattern at {s:#x}: add={add_a} clr={clr_a}'
    for a in range(add_a + 4, s, 4):
        if a == clr_a: continue
        assert not ({9, 31, B_} & regs_written(W(a))), f'r9/r31/base clobbered between at {a:#x}'
    put(add_a, lwz(9, EXT, B_))
    put(clr_a, add(9, 9, 31))
    put(s, lwz(T, 0, 9))
    print(f'P2 {s:#x}: base r{B_}')
    # bound: the next cmpwi cr7,r31,8 within 12 instrs
    for k in range(1, 12):
        a = s + 4 * k
        if W(a) == cmpwi(7, 31, 8):
            put(a, cmpwi(7, 31, 8 * (NWIN - 1))); break
    else:
        raise AssertionError(f'no cmpwi r31,8 after {s:#x}')

# 0x460cc0's function reads the slot twice
put(0x460d74, lwz(4, 0, 26), expect=lwz(4, 0xc, 26))

# --- P3: addi r31,r3,0x1c loops + count bounds
for a in (0x45fe50, 0x4601dc, 0x460284, 0x4605e8, 0x460880, 0x4608fc):
    put(a, lwz(31, EXT, 3), expect=addi(31, 3, 0x1c))
for a, r in {0x45fe70: 30, 0x460230: 30, 0x4602b0: 30, 0x460648: 29, 0x4608a0: 30, 0x460938: 30,
             0x45f3bc: 31, 0x45f4e0: 31, 0x45f7c4: 31, 0x4609d0: 31, 0x460a44: 31}.items():
    put(a, cmpwi(7, r, NWIN - 1), expect=cmpwi(7, r, 1))

# --- setWindowMax 0x460814 (21 words available)
sw = 0x460814
body = [stw(4, 0x2c, 3), lwz(10, EXT, 3), li(8, 0),
        lwz(9, 0, 10), cmpw(7, 8, 4), li(0, 1), None, li(0, 0), stb(0, 0xc, 9),
        addi(10, 10, 8), addi(8, 8, 1), cmpwi(7, 8, NWIN), None, 0x4E800020]
body[6] = blt(sw + 4 * 6, sw + 4 * 8)
body[12] = bne(sw + 4 * 12, sw + 4 * 3)
for i, x in enumerate(body): put(sw + 4 * i, x)
for i in range(len(body), 21): put(sw + 4 * i, nop())

# --- WM constructor cave: hook at 0x462124 (li r9,1), replicate the tail, return to 0x46215c
c = CAVE
cave = [
    li(3, 0x40), bl(c + 4, ALLOC),
    mr(31, 3), stw(31, EXT, 29),
    lwz(0, 0x1c, 29), stw(0, 0, 31), lwz(0, 0x20, 29), stw(0, 4, 31),
    lwz(0, 0x24, 29), stw(0, 8, 31), lwz(0, 0x28, 29), stw(0, 0xc, 31),
]
def win(idx, slot):
    global c
    base = c + 4 * len(cave)
    seq = [li(3, 0x740), bl(base + 4, ALLOC), mr(30, 3), li(4, idx), bl(base + 16, WIN_CTOR), stw(30, slot, 31)]
    cave.extend(seq)
win(2, 0x10); win(3, 0x18)
cave += [lis(8, NODE >> 16), ori(8, 8, NODE & 0xffff), stw(8, 0x14, 31), stw(8, 0x1c, 31),
         # original tail 0x462124..0x462158
         li(9, 1), li(0, 0), stw(9, 0x30, 29), stw(9, 0x2c, 29), lis(9, 0x180), li(11, 0),
         stb(0, 0x39, 29), stb(0, 0x34, 29), stb(0, 0x35, 29), stb(0, 0x36, 29), stb(0, 0x37, 29), stb(0, 0x38, 29),
         stw(11, -0x2f4c, 9), stb(11, 0x18, 29)]
cave.append(b(c + 4 * len(cave), 0x46215c))
for i, x in enumerate(cave):
    assert W(c + 4 * i) == 0, 'cave not empty'
    put(c + 4 * i, x)
put(0x462124, b(0x462124, CAVE), expect=0x39200001)

# verify original tail words we replicate
for a, e in [(0x462128, 0x38000000), (0x46212c, 0x913D0030), (0x462130, 0x913D002C), (0x462134, 0x3D200180),
             (0x462138, 0x39600000), (0x46213c, 0x981D0039), (0x462140, 0x981D0034), (0x462154, 0x9169D0B4), (0x462158, 0x997D0018)]:
    assert W(a) == e, f'tail mismatch at {a:#x}: {W(a):08X}'

lines = []
for a in sorted(out):
    lines.append(f'0x{a:08x} {W(a):08X} {out[a]:08X}')
    print(f'{a:08x} {W(a):08X} -> {out[a]:08X}  {dis(a, out[a])}')
open('/home/sebastian/gt5re/win4_words.txt', 'w').write('\n'.join(lines) + '\n')
print(len(out), 'words -> win4_words.txt')
