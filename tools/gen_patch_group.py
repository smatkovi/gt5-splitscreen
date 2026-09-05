#!/usr/bin/env python3
"""Emit one RPCS3 patch group (patch.yml syntax, for the PPU hash of the unpatched 2.17 EBOOT) from
GT5 word lists.  Usage: gen_patch_group.py "<title>" "<notes>" <words.txt> [...]  (prints YAML)"""
import sys
title, notes, files = sys.argv[1], sys.argv[2], sys.argv[3:]
words = []
for fn in files:
    for l in open(fn):
        p = l.split()
        if len(p) == 3: words.append((int(p[0], 16), int(p[2], 16)))
        elif len(p) == 2: words.append((int(p[0], 16), int(p[1], 16)))
out = [f'  "{title}":', '    Games:', '      "Gran Turismo 5":', '        BCES00569: [ 02.17 ]',
       '    Author: "gt5re"', f'    Notes: "{notes}"', '    Patch Version: 1.0', '    Patch:']
out += [f'      - [ be32, 0x{a:08x}, 0x{w:08X} ]' for a, w in sorted(words)]
print('\n'.join(out) + '\n')
