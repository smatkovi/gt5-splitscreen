#!/usr/bin/env python3
"""Generate keycfg4_words.txt: let gtengine::MController hold key configurations for controller
ports 2 and 3.

Background (GT5 2.17 EBOOT, load base 0x10000):
  The controller-config context is a static aggregate at 0x17FDF60.  It holds exactly two per-port
  handles {vtable 0x16EB0B0, &config_vector} at +0x10/+0x18 and the two config vectors inline in the
  context object (+0x24, +0x34).  The getter 0x48A8F4 (vtable slot 0x10 of the context) returns
  &handle[port] and NULL for port > 1; MController::declare/getConfig/setConfig and the per-player
  input mapping all go through it, so pads 3 and 4 never get a button mapping (their SuperPort
  handles exist, the input is polled, but nothing maps it to accelerate/brake/steer).

Patch:
  * two more handles + two config vectors live in the unused tail of the RW data segment
    (memsz ends at 0x19485B0, the page is mapped up to 0x1950000): NEW = 0x1948600,
    handles at +0x00/+0x08, vectors at +0x10/+0x20.
  * the static constructor (0x48A9D4) gets a cave after the port-1 handle init (0x48ABA8) that
    constructs the two vectors (0x48BD30, same vtable arg 0x16B6720 as the originals) and the
    handles (0x48AF24).
  * the getter accepts port <= 3; ports 2/3 are routed to NEW via a small cave.
Output format: "0xADDR ORIGWORD NEWWORD" (build_eboot.sh / deploy scripts), capstone-verified.
"""
import struct, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ppcasm import *  # noqa

BASE = pathlib.Path(__file__).resolve().parent.parent
elf = (BASE / 'EBOOT.elf').read_bytes()
def orig(a): return struct.unpack('>I', elf[a - 0x10000:a - 0x10000 + 4])[0]

NEW = 0x1948600                 # 0x30 bytes: handle2, handle3, vec2 (0x10), vec3 (0x10)
CAVE_ALT = 0x1581100            # getter (whole function), ports 0..3
CAVE_INIT = 0x1581140           # static-ctor extension
VEC_CTOR, HANDLE_INIT = 0x48bd30, 0x48af24
VT_VEC = 0x16b6720
def hi(v): return (v + 0x8000) >> 16
def lo(v): return ((v + 0x8000) & 0xffff) - 0x8000

words = []
def put(a, w): words.append((a, w))

# --- getter 0x48A8F4: r4 = port -> r3 = &handle[port] or 0.  The whole function moves into the
# cave (conditional branches only reach +-32 KiB); the first original word becomes "b CAVE_ALT".
put(0x48a8f4, b(0x48a8f4, CAVE_ALT))
c = CAVE_ALT
seq = [cmplwi(7, 4, 3), li(3, 0), bgt(c + 8, c + 36), slwi(3, 4, 3), cmplwi(7, 4, 1),
       lis(9, 0x180), addi(9, 9, -0x2090), bgt(c + 28, c + 40), add(3, 3, 9), blr(),
       lis(9, hi(NEW - 0x10)), addi(9, 9, lo(NEW - 0x10)), add(3, 3, 9), blr()]
for i, w in enumerate(seq): put(c + i * 4, w)
assert c + len(seq) * 4 <= CAVE_INIT

# --- static ctor: 0x48ABA8 "bl 0x48AF24" (port-1 handle) -> b CAVE_INIT
assert orig(0x48aba8) == bl(0x48aba8, HANDLE_INIT)
put(0x48aba8, b(0x48aba8, CAVE_INIT))
c = CAVE_INIT
body = [('bl', HANDLE_INIT)]
for vec in (NEW + 0x10, NEW + 0x20):
    body += [lis(3, hi(vec)), addi(3, 3, lo(vec)), lis(4, hi(VT_VEC)), addi(4, 4, lo(VT_VEC)), ('bl', VEC_CTOR)]
for h, vec in ((NEW, NEW + 0x10), (NEW + 8, NEW + 0x20)):
    body += [lis(3, hi(h)), addi(3, 3, lo(h)), lis(4, hi(vec)), addi(4, 4, lo(vec)), ('bl', HANDLE_INIT)]
body += [('b', 0x48abac)]
for i, w in enumerate(body):
    pc = c + i * 4
    if isinstance(w, tuple): w = bl(pc, w[1]) if w[0] == 'bl' else b(pc, w[1])
    put(pc, w)
assert c + len(body) * 4 <= 0x1581200

out = BASE / 'keycfg4_words.txt'
with open(out, 'w') as f:
    for a, w in words:
        f.write(f'0x{a:08x} {orig(a):08X} {w:08X}\n')
print(out, len(words), 'words')
show(words)
