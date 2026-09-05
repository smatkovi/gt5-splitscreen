import struct, re, sys
d=open('EBOOT.elf','rb').read()
segs=[(0x0,0x10000,0x169e6e8),(0x16a0000,0x16b0000,0x11f9d8)]
def off2va(o):
    for fo,va,sz in segs:
        if fo<=o<fo+sz: return va+(o-fo)
def va2off(v):
    for fo,va,sz in segs:
        if va<=v<va+sz: return fo+(v-va)
def refs(va):
    return [off2va(m.start()) for m in re.finditer(re.escape(struct.pack('>I',va)),d) if m.start()%4==0]
name=sys.argv[1].encode()
for m in re.finditer(re.escape(name)+b'\x00',d):
    o=m.start()
    if o>0 and d[o-1]!=0: continue
    sva=off2va(o); 
    for ti in refs(sva):
        ti-=4  # typeinfo object: [vptr, name_ptr, ...]
        print('typeinfo', hex(ti))
        for vt in refs(ti):
            vstart=vt+4
            print('  vtable funcs at', hex(vstart))
            o2=va2off(vstart); fn=[]
            for k in range(40):
                p=struct.unpack('>I',d[o2+4*k:o2+4*k+4])[0]
                if not (0x16b0000<=p<0x17cfa00): break
                # function descriptor -> entry
                po=va2off(p); entry=struct.unpack('>I',d[po:po+4])[0] if po else 0
                fn.append(hex(entry))
            print('   ', ' '.join(fn))
