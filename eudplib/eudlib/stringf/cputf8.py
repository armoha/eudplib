#!/usr/bin/python
# -*- coding: utf-8 -*-


from ..eudarray import EUDArray

from ...ctrlstru import EUDInfLoop, EUDEndInfLoop, EUDIf, EUDElse, EUDEndIf, EUDBreakIf
from .rwcommon import br1, bw1
from .cp949_table import cp949_table

"""
KSC5601 -> Unicode 2.0 mapping table, compressed for the 94*94 codeset.
Generated based on  KSC5601.txt at
  ftp://ftp.unicode.org/Public/MAPPINGS/EASTASIA/KSC

Unlike kuten-table, needed offset is 33 (0x21) instead of
32 for 7-bit portion of each byte.  i.e., a Unicode
codepoint for KSC's codepoint (n, m) would be found at
index (n-33)*94+m-33.
"""


# Create conversion table
cvtb = [0] * 65536
for (ch1, ch2), tab in cp949_table:
    cvtb[ch1 + ch2 * 256] = tab
cvtb = EUDArray(cvtb)


def f_cp949_to_utf8_cpy(dst, src):
    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if EUDInfLoop()():
        b1 = br1.readbyte()
        EUDBreakIf(b1 == 0)
        if EUDIf()(b1 < 128):
            bw1.writebyte(b1)
        if EUDElse()():
            b2 = br1.readbyte()
            EUDBreakIf(b2 == 0)
            code = cvtb[b2 * 256 + b1]
            if EUDIf()(code <= 0x07FF):
                # Encode as 2-byte
                bw1.writebyte(0b11000000 | (code // (1 << 6)) & 0b11111)
                bw1.writebyte(0b10000000 | (code // (1 << 0)) & 0b111111)
            if EUDElse()():
                # Encode as 3-byte
                bw1.writebyte(0b11100000 | (code // (1 << 12)) & 0b1111)
                bw1.writebyte(0b10000000 | (code // (1 << 6)) & 0b111111)
                bw1.writebyte(0b10000000 | (code // (1 << 0)) & 0b111111)
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()
    bw1.writebyte(0)
