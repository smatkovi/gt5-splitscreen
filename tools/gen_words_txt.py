#!/usr/bin/env python3
"""Merge word lists into a release words.txt: address, original word, new word, disassembly of both
(capstone), grouped by source file.  Usage: gen_words_txt.py <out> <label:file> [...]"""
import sys
sys.path.insert(0, '/home/sebastian/gt5re/tools')
from ppcasm import dis
out = sys.argv[1]
lines = ['# GT5 BCES00569 2.17 (decrypted EBOOT sha1 306f86c62b9f03041c903be96ac59e5c3f130452, load base 0x10000)',
         '# address  original  new       original-disasm            new-disasm',
         '# original == 00000000 marks code-cave words (free zeroed R-X memory).', '']
total = 0
for spec in sys.argv[2:]:
    label, fn = spec.split(':', 1)
    lines.append(f'## {label}  ({fn})')
    for l in open(fn):
        p = l.split()
        if len(p) == 3: a, o, n = int(p[0], 16), int(p[1], 16), int(p[2], 16)
        elif len(p) == 2: a, o, n = int(p[0], 16), 0, int(p[1], 16)
        else: continue
        lines.append(f'{a:08x}  {o:08X}  {n:08X}  {dis(a, o) if o else "(cave)":26s} {dis(a, n)}')
        total += 1
    lines.append('')
open(out, 'w').write('\n'.join(lines) + '\n')
print(out, total, 'words')
