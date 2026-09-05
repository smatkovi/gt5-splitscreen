import struct, sys
from capstone import *
d = open('EBOOT.elf','rb').read()
segs = [(0x0, 0x10000, 0x169e6e8), (0x16a0000, 0x16b0000, 0x11f9d8)]
def va2off(v):
    for fo, va, sz in segs:
        if va <= v < va+sz: return fo + (v-va)
md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
md.detail = False
md.skipdata = True
def dis(start, count):
    o = va2off(start)
    hi = None
    for i in md.disasm(d[o:o+count*4], start):
        s = f'{i.address:08x}  {i.mnemonic:8s} {i.op_str}'
        # annotate lis/addi pairs
        if i.mnemonic == 'lis':
            r, v = i.op_str.split(', '); hi = (r, int(v, 0) & 0xffff)
        elif i.mnemonic in ('addi','ori','li') and hi:
            parts = i.op_str.split(', ')
            if len(parts) == 3 and parts[1] == hi[0]:
                v = int(parts[2], 0)
                addr = ((hi[1] << 16) + v) & 0xffffffff if i.mnemonic == 'addi' else (hi[1] << 16) | (v & 0xffff)
                oo = va2off(addr)
                txt = ''
                if oo is not None:
                    seg = d[oo:oo+40]
                    if all(32 <= c < 127 for c in seg[:4]):
                        txt = '"' + seg.split(b'\0')[0][:40].decode('latin1') + '"'
                s += f'    ; 0x{addr:x} {txt}'
        print(s)
if __name__ == '__main__':
    dis(int(sys.argv[1],16), int(sys.argv[2]))
