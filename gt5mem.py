#!/usr/bin/env python3
"""
Liest Organizer und Auto-Slots aus dem laufenden GT5-Prozess und schreibt sie
in eine Textdatei, die sich zwischen zwei Laeufen vergleichen laesst.

  Voraussetzung: PS3=<ip> gesetzt, GT5 laeuft, und der Zeiger steht in der
  Ablage (leak_a.sh im Hauptmenue, Rennen starten, leak_b.sh).

  python3 gt5mem.py dump referenz         # Organizer+Slots -> gt5dump_referenz.txt
  python3 gt5mem.py dump split3
  python3 gt5mem.py diff gt5dump_referenz.txt gt5dump_split3.txt

  Optionen:  --org 0x4FEB9000    Objektadresse direkt angeben
             --scratch 0x19485A0 Ablage, aus der der Zeiger gelesen wird
             --slotbytes 1600    wieviel je Slot gedumpt wird (0x640 = 1600)
"""
import argparse, os, re, sys, urllib.request

TAGS = re.compile(r'<[^>]+>')
ROW  = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2}\s+){1,16})')

# Zeiger in diese Bereiche werden im Diff maskiert - sie unterscheiden sich
# zwischen zwei Laeufen zwangslaeufig und sagen nichts aus.
HEAP = [(0x10000000, 0x60000000), (0x40000000, 0x60000000)]


def get(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode('latin1')


class PS3:
    def __init__(self, ip):
        self.ip = ip
        page = get(f'http://{ip}/home.ps3mapi')
        m = re.search(r'proc=(0x[0-9a-fA-F]+)', page)
        if not m:
            sys.exit('kein Spielprozess gefunden - laeuft GT5?')
        self.pid = m.group(1)

    def read(self, addr, length):
        """Liest length Bytes ab addr, in Haeppchen von 256."""
        out = bytearray()
        pos = 0
        while pos < length:
            n = min(256, length - pos)
            html = get(f'http://{self.ip}/getmem.ps3mapi?'
                       f'proc={self.pid}&addr=0x{addr+pos:x}&len={n}')
            text = TAGS.sub('\n', html)
            got = {}
            for m in ROW.finditer(text):
                rowaddr = int(m.group(1), 16)
                data = bytes.fromhex(m.group(2).replace(' ', '').replace('\n', ''))
                got[rowaddr] = data
            chunk = bytearray()
            a = addr + pos
            while len(chunk) < n:
                base = a & ~0xF
                if base not in got:
                    break
                row = got[base]
                off = a - base
                take = min(16 - off, n - len(chunk))
                chunk += row[off:off + take]
                a += take
            if not chunk:
                break
            out += chunk
            pos += len(chunk)
        return bytes(out)


def u32(b, off):
    return int.from_bytes(b[off:off + 4], 'big')


def hexdump(data, base, mask=False):
    lines = []
    for i in range(0, len(data), 16):
        row = data[i:i + 16]
        words = []
        for j in range(0, len(row), 4):
            w = row[j:j + 4]
            if len(w) == 4 and mask:
                v = int.from_bytes(w, 'big')
                if any(lo <= v < hi for lo, hi in HEAP):
                    words.append('~~~~~~~~')
                    continue
            words.append(w.hex().upper())
        lines.append(f'  +{i:04X}  ' + ' '.join(words))
    return lines


def cmd_dump(args):
    ip = os.environ.get('PS3') or sys.exit('PS3=<ip> setzen')
    ps3 = PS3(ip)
    print(f'pid={ps3.pid}')

    if args.org:
        org = int(args.org, 16)
    else:
        v = ps3.read(int(args.scratch, 16), 4)
        org = int.from_bytes(v, 'big')
        if not org:
            sys.exit('Ablage ist leer - erst leak_a.sh / Rennen / leak_b.sh')
    print(f'Organizer @ 0x{org:08X}')

    head = ps3.read(org, 0xA00)
    cnt = u32(head, 0x984)
    arr = u32(head, 0x234)
    print(f'  slotcount +0x984 = {cnt}')
    print(f'  slotarray +0x234 = 0x{arr:08X}')
    if cnt > 32 or arr == 0:
        sys.exit('unplausibel - falsche Objektadresse?')

    out = [f'# GT5 Speicherabbild: {args.label}',
           f'# Organizer 0x{org:08X}  slots={cnt}  array=0x{arr:08X}',
           '', '== Organizer (0x000-0xA00, Zeiger maskiert) ==']
    out += hexdump(head, org, mask=True)

    for i in range(cnt):
        s = arr + i * 0x640
        data = ps3.read(s, args.slotbytes)
        car = u32(data, 0x0C)
        done = data[0x10]
        out += ['', f'== Slot {i} @ 0x{s:08X}  auto=0x{car:08X}  fertig={done} ==']
        out += hexdump(data, s, mask=True)
        print(f'  slot {i}: auto=0x{car:08X} +0x10={done} +0x12={data[0x12]} +0x1D={data[0x1D]}')

    path = f'gt5dump_{args.label}.txt'
    open(path, 'w').write('\n'.join(out) + '\n')
    print(f'-> {path}  ({len(out)} Zeilen)')


def cmd_diff(args):
    a = open(args.a).read().split('\n')
    b = open(args.b).read().split('\n')
    import difflib
    n = 0
    for line in difflib.unified_diff(a, b, args.a, args.b, lineterm='', n=1):
        print(line)
        n += 1
    if n == 0:
        print('identisch')


p = argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest='cmd', required=True)
d = sub.add_parser('dump'); d.add_argument('label')
d.add_argument('--org'); d.add_argument('--scratch', default='0x19485A0')
d.add_argument('--slotbytes', type=int, default=0x640)
d.set_defaults(func=cmd_dump)
f = sub.add_parser('diff'); f.add_argument('a'); f.add_argument('b')
f.set_defaults(func=cmd_diff)
args = p.parse_args()
args.func(args)
