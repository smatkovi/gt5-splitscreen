#!/usr/bin/env python3
"""
Tastet NUR Slot 2 und den offen-Zaehler mit hoher Frequenz ab, um zu sehen,
ob ein Worker den dritten Auftrag jemals anfasst.

  PS3=192.168.1.11 python3 watch2.py            # Organizer 0x4FEB9000, Slot 2

Vor dem Split-Battle starten. Zeigt jede Aenderung an slot2.zustand / f510 / +0x28
und am offen-Zaehler. Bleibt zustand dauerhaft 22, hat kein Worker ihn je genommen.
Blitzt er kurz auf 13 (0xd) oder 9, hat ein Worker ihn genommen und ist ausgestiegen.
"""
import argparse, os, re, sys, time, urllib.request
TAGS = re.compile(r'<[^>]+>'); ROW = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2}\s+){1,16})')

def get(url, t=15, tries=4):
    last=None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=t) as r: return r.read().decode('latin1')
        except Exception as e: last=e; time.sleep(0.3)
    raise last

class PS3:
    def __init__(s, ip):
        s.ip=ip
        m=re.search(r'proc=(0x[0-9a-fA-F]+)', get(f'http://{ip}/home.ps3mapi'))
        if not m: sys.exit('kein Spielprozess'); 
        s.pid=m.group(1)
    def rd(s, addr, n):
        html=get(f'http://{s.ip}/getmem.ps3mapi?proc={s.pid}&addr=0x{addr:x}&len={n}')
        mem={}
        for m in ROW.finditer(TAGS.sub('\n',html)):
            base=int(m.group(1),16); data=bytes.fromhex(m.group(2).replace(' ','').replace('\n',''))
            for k,b in enumerate(data): mem[base+k]=b
        out=bytearray(); a=addr
        while len(out)<n and a in mem: out.append(mem[a]); a+=1
        return bytes(out)
    def u32(s, a): 
        b=s.rd(a,4); return int.from_bytes(b,'big') if len(b)==4 else None

p=argparse.ArgumentParser(); p.add_argument('--org',default='0x4FEB9000'); p.add_argument('--slot',type=int,default=2)
a=p.parse_args()
ip=os.environ.get('PS3') or sys.exit('PS3=<ip> setzen')
ps3=PS3(ip); org=int(a.org,16)
print(f'pid={ps3.pid}  warte auf Rennen...')
while True:
    arr=ps3.u32(org+0x234); cnt=ps3.u32(org+0x984)
    if arr and cnt and 0<cnt<=32: break
    time.sleep(0.3)
s=arr+a.slot*0x640
print(f'Slot {a.slot} @ 0x{s:08X}  -- schnelle Abtastung (Strg-C beendet)\n')
prev=None; t0=time.time()
try:
    while True:
        zu=ps3.u32(s+0x4f4); f510=ps3.u32(s+0x510); j=None
        st=(zu,f510)
        if st!=prev:
            print(f'{time.time()-t0:6.2f}s  zustand={zu} f510={f510} offen={ps3.u32(org+0x288)}')
            prev=st
        time.sleep(0.05)
except KeyboardInterrupt:
    print('\nletzter Zustand:', prev)
