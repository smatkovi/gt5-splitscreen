import struct, sys
d = open('EBOOT.elf','rb').read()
CODE_FO, CODE_VA, CODE_SZ = 0x200, 0x10200, 0x0f8e48c+0x9df0+0x24+0x2c
code = d[CODE_FO:CODE_FO+CODE_SZ]
n = len(code)//4
ins = struct.unpack('>%dI' % n, code[:n*4])
def refs(target):
    hi = ((target + 0x8000) >> 16) & 0xffff
    lo = target & 0xffff
    out = []
    for i, w in enumerate(ins):
        if (w >> 26) == 15 and ((w >> 16) & 31) == 0 and (w & 0xffff) == hi:   # lis rD, hi
            rD = (w >> 21) & 31
            for j in range(i+1, min(i+12, n)):
                w2 = ins[j]
                op = w2 >> 26
                if op == 14 and ((w2 >> 16) & 31) == rD and (w2 & 0xffff) == lo:   # addi rX, rD, lo
                    out.append(CODE_VA + j*4); break
                # ori rD, rD, lo (unsigned form)
                if op == 24 and ((w2 >> 21) & 31) == rD and (w2 & 0xffff) == (target & 0xffff) and hi == (target >> 16):
                    out.append(CODE_VA + j*4); break
                if op == 15 and ((w2 >> 21) & 31) == rD: break
    return out
for a in sys.argv[1:]:
    t = int(a, 16)
    print(hex(t), [hex(x) for x in refs(t)])
