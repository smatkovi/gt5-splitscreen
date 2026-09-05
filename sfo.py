import struct, sys
d = open(sys.argv[1], 'rb').read()
magic, ver, koff, doff, n = struct.unpack_from('<4sIIII', d, 0)
for i in range(n):
    ko, fmt, dlen, dmax, do = struct.unpack_from('<HHIII', d, 20 + 16*i)
    key = d[koff+ko:d.index(b'\0', koff+ko)].decode()
    val = d[doff+do:doff+do+dlen]
    if fmt == 0x0404:
        val = struct.unpack('<I', val)[0]
    else:
        val = val.rstrip(b'\0').decode('utf-8', 'replace')
    print(f'{key:16} {val}')
