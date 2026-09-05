#!/usr/bin/env python3
"""
Verfolgt Slot 0/1/2 (zustand, f510) und den offen-Zaehler gemeinsam, sanft genug
fuer webMANs Webserver. Ziel: den Moment einfangen, in dem Slot 2 nach Zustand 11
wieder auf 22 zurueckfaellt - und was gleichzeitig an offen/Slot0/1 passiert.

  PS3=192.168.1.11 python3 watch3.py

Vor dem Split-Battle starten. Laeuft weiter, auch wenn webMAN mal einen Request
abwirft (zaehlt Aussetzer, stirbt nicht). Strg-C fuer Zusammenfassung.
"""
import os, re, sys, time, urllib.request
TAGS = re.compile(r'<[^>]+>'); ROW = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2}\s+){1,16})')

def get(url, t=15):
    with urllib.request.urlopen(url, timeout=t) as r:
        return r.read().decode('latin1')

class PS3:
    def __init__(s, ip):
        s.ip=ip
        s.pid=re.search(r'proc=(0x[0-9a-fA-F]+)', get(f'http://{ip}/home.ps3mapi')).group(1)
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

ip=os.environ.get('PS3') or sys.exit('PS3=<ip> setzen')
org=int((sys.argv[1] if len(sys.argv)>1 else '0x4FEB9000'),16)
ps3=PS3(ip)
print(f'pid={ps3.pid}  warte auf Rennen...')
while True:
    try:
        arr=ps3.u32(org+0x234); cnt=ps3.u32(org+0x984)
        if arr and cnt and 0<cnt<=32: break
    except Exception: pass
    time.sleep(0.3)
print(f'Slots={cnt}  Array=0x{arr:08X}  -- Abtastung ~0.2s (Strg-C beendet)\n')

def state():
    v={'offen': ps3.u32(org+0x288)}
    for i in range(min(cnt,3)):
        s=arr+i*0x640
        v[f's{i}z']=ps3.u32(s+0x4f4); v[f's{i}r']=ps3.u32(s+0x510)
    return v

prev=None; t0=time.time(); drops=0; s2_reached11=False
try:
    while True:
        try:
            v=state()
        except Exception:
            drops+=1; time.sleep(0.5); continue
        if v.get('s2z')==11: s2_reached11=True
        if v!=prev:
            line=f'{time.time()-t0:6.2f}s  offen={v["offen"]}'
            for i in range(min(cnt,3)):
                line+=f'  s{i}:z={v[f"s{i}z"]},r={v[f"s{i}r"]}'
            print(line); prev=v
        time.sleep(0.2)
except KeyboardInterrupt:
    print(f'\nSlot2 hat Zustand 11 erreicht: {"JA" if s2_reached11 else "nein"}   (Aussetzer: {drops})')
