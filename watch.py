#!/usr/bin/env python3
"""
Beobachtet die Auto-Slots waehrend des Ladens und schreibt jede Zustandsaenderung
mit Zeitstempel mit. Damit sieht man, in welcher Reihenfolge die Felder kippen.

  PS3=192.168.1.11 python3 watch.py            # Standard: Organizer 0x4FEB9000
  PS3=192.168.1.11 python3 watch.py --org 0x4FEB9000 --interval 1.0

Waehrend des Ladens starten - im Referenzrennen (viele KI-Autos) sieht man
16 saubere Uebergaenge, im Split-Lauf bleibt einer haengen.
Beenden mit Strg-C; danach wird eine Zusammenfassung gedruckt.
"""
import argparse, os, re, sys, time, urllib.request

TAGS = re.compile(r'<[^>]+>')
ROW = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2}\s+){1,16})')

# Felder, die wir verfolgen: (Offset, Breite, Name)
FIELDS = [
    (0x004, 4, 'f04'),
    (0x00C, 4, 'auto'),
    (0x010, 1, 'fertig'),
    (0x012, 1, 'angef'),
    (0x01D, 1, 'bereit'),
    (0x4F4, 4, 'zustand'),
    (0x4F8, 4, 'index'),
    (0x510, 4, 'f510'),
]


def get(url, timeout=20, tries=3):
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read().decode('latin1')
        except Exception as e:            # webMAN schliesst gelegentlich einfach
            last = e
            time.sleep(0.4)
    raise last


class PS3:
    def __init__(self, ip):
        self.ip = ip
        m = re.search(r'proc=(0x[0-9a-fA-F]+)', get(f'http://{ip}/home.ps3mapi'))
        if not m:
            sys.exit('kein Spielprozess - laeuft GT5?')
        self.pid = m.group(1)

    def read(self, addr, n):
        """Liest n Bytes ab addr. webMAN beschriftet Zeilen mal mit dem
        16er-Blockanfang, mal mit der angefragten Adresse - deshalb bauen
        wir eine Byte-Karte statt auf Ausrichtung zu vertrauen."""
        out = bytearray()
        pos = 0
        while pos < n:
            want = min(256, n - pos)
            html = get(f'http://{self.ip}/getmem.ps3mapi?'
                       f'proc={self.pid}&addr=0x{addr+pos:x}&len={want}')
            mem = {}
            for m in ROW.finditer(TAGS.sub('\n', html)):
                base = int(m.group(1), 16)
                data = bytes.fromhex(m.group(2).replace(' ', '').replace('\n', ''))
                for k, b in enumerate(data):
                    mem[base + k] = b
            got = bytearray()
            a = addr + pos
            while len(got) < want and a in mem:
                got.append(mem[a])
                a += 1
            if not got:
                break
            out += got
            pos += len(got)
        return bytes(out)


def snapshot(ps3, arr, i):
    """Zwei Leseoperationen je Slot: Kopf und Zustandsblock."""
    s = arr + i * 0x640
    head = ps3.read(s, 0x20)
    tail = ps3.read(s + 0x4F0, 0x30)
    if len(head) < 0x20 or len(tail) < 0x30:
        return None
    v = {}
    for off, w, name in FIELDS:
        blk, base = (head, 0) if off < 0x20 else (tail, 0x4F0)
        o = off - base
        v[name] = int.from_bytes(blk[o:o + w], 'big')
    return v


def org_snapshot(ps3, org, cnt):
    """Fortschrittszaehler und die Slot-Indizes der Auftraege."""
    blk = ps3.read(org + 0x980, 0x20)          # +0x980 .. +0x99F
    if len(blk) < 0x20:
        return None
    v = {}
    for k in range(7):
        v[f'z{0x980 + k*4:03x}'] = int.from_bytes(blk[k*4:k*4+4], 'big')
    v['offen'] = int.from_bytes(ps3.read(org + 0x288, 4), 'big')
    jobs = int.from_bytes(ps3.read(org + 0xBD8, 4), 'big')
    if jobs:
        for i in range(min(cnt, 8)):
            j = int.from_bytes(ps3.read(jobs + i*0x34 + 0x28, 4), 'big')
            v[f'job{i}'] = j if j != 0xFFFFFFFF else -1
    return v


def fmt(d):
    parts = []
    for k, val in d.items():
        parts.append(f'{k}=0x{val:X}' if k == 'auto' else f'{k}={val}')
    return ' '.join(parts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--org', default='0x4FEB9000')
    p.add_argument('--interval', type=float, default=1.0)
    a = p.parse_args()

    ip = os.environ.get('PS3') or sys.exit('PS3=<ip> setzen')
    ps3 = PS3(ip)
    org = int(a.org, 16)
    print(f'pid={ps3.pid}  Organizer=0x{org:08X}')
    print('Warte auf ein Rennen... (Strg-C beendet)')
    cnt = arr = 0
    try:
        while True:
            cnt = int.from_bytes(ps3.read(org + 0x984, 4), 'big')
            arr = int.from_bytes(ps3.read(org + 0x234, 4), 'big')
            if 0 < cnt <= 32 and arr:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)
    print(f'Slots={cnt}  Array=0x{arr:08X}  -- Beobachtung laeuft\n')

    prev = {}
    t0 = time.time()
    try:
        while True:
            o = org_snapshot(ps3, org, cnt)
            if o is not None:
                if 'org' not in prev:
                    print(f'{time.time()-t0:6.1f}s  ORG           {fmt(o)}')
                elif o != prev['org']:
                    ch = ' '.join(f'{k}:{prev["org"][k]}->{o[k]}'
                                  for k in o if o[k] != prev['org'][k])
                    print(f'{time.time()-t0:6.1f}s  ORG           {ch}')
                prev['org'] = o

            for i in range(cnt):
                v = snapshot(ps3, arr, i)
                if v is None:
                    continue
                if i not in prev:
                    print(f'{time.time()-t0:6.1f}s  slot {i:2d}  START  {fmt(v)}')
                elif v != prev[i]:
                    ch = ' '.join(f'{k}:{prev[i][k]}->{v[k]}'
                                  for k in v if v[k] != prev[i][k])
                    print(f'{time.time()-t0:6.1f}s  slot {i:2d}         {ch}')
                prev[i] = v
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print('\n--- Endzustand ---')
        if 'org' in prev:
            print(f'ORG     {fmt(prev.pop("org"))}')
        for i in sorted(prev):
            print(f'slot {i:2d}  {fmt(prev[i])}')


main()
