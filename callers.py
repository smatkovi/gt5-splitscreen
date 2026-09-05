import struct, sys
d=open('EBOOT.elf','rb').read()
CODE_FO, CODE_VA = 0x200, 0x10200
code=d[CODE_FO:CODE_FO+0x0f9e6e0-0x200]
n=len(code)//4
ins=struct.unpack('>%dI'%n, code[:n*4])
targets={int(a,16):[] for a in sys.argv[1:]}
for i,w in enumerate(ins):
    if (w>>26)==18 and (w&1) and not (w&2):  # bl
        li=w&0x03fffffc
        if li&0x02000000: li-=0x04000000
        t=CODE_VA+i*4+li
        if t in targets: targets[t].append(CODE_VA+i*4)
for t,c in targets.items(): print(hex(t), [hex(x) for x in c])
