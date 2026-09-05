#!/usr/bin/env python3
"""Post-process a scetool-built NPDRM SELF: set the digest's firmware version (scetool leaves it
0 when a template is used; the original GT5 2.17 EBOOT says 4.10 = 41000) and verify both NPDRM
OMAC hashes independently (pycryptodome).  The CID_FN hash depends only on content id, file name
and the NP_tid key, so it must equal the original EBOOT's 6f6c156c002897e0c5fb477bdd8e0896."""
import struct, sys
from Crypto.Hash import CMAC
from Crypto.Cipher import AES

NP_TID = bytes.fromhex('9B515FEACF75064981AA604D91A54E97')   # RPCS3 NP_OMAC_KEY_3
NP_CI = bytes.fromhex('6BA52976EFDA16EF3C339FB2971E256B')    # RPCS3 NP_OMAC_KEY_2
KLIC_FREE = bytes.fromhex('72F990788F9CFF745725F08E4C128387')
ORIG_CID_FN = '6f6c156c002897e0c5fb477bdd8e0896'

p = sys.argv[1]
d = bytearray(open(p, 'rb').read())
ctrl = struct.unpack('>Q', d[0x20 + 7 * 8:0x20 + 8 * 8])[0]     # SELF header: control info offset
fw_off = ctrl + 0x30 + 0x10 + 0x28                               # flags(0x30) + digest hdr(0x10) + 2*sha1
d[fw_off:fw_off + 8] = struct.pack('>Q', 41000)
np_hdr = ctrl + 0x30 + 0x40
body = np_hdr + 0x10
assert d[body:body + 4] == b'NPD\x00', f'no NPDRM control info at {body:#x}: {bytes(d[body:body+4])!r}'
cid = bytes(d[body + 0x10:body + 0x40])
m = CMAC.new(NP_TID, ciphermod=AES); m.update(cid + b'EBOOT.BIN')
got = bytes(d[body + 0x50:body + 0x60]).hex()
assert m.hexdigest() == got == ORIG_CID_FN, f'CID_FN hash mismatch: file {got} computed {m.hexdigest()}'
m = CMAC.new(bytes(a ^ b for a, b in zip(NP_CI, KLIC_FREE)), ciphermod=AES); m.update(bytes(d[body:body + 0x60]))
got = bytes(d[body + 0x60:body + 0x70]).hex()
assert m.hexdigest() == got, f'CI hash mismatch: file {got} computed {m.hexdigest()}'
open(p, 'wb').write(d)
print('fw_version set to 4.10, NPDRM hashes verified:', p)
