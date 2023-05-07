#!/usr/bin/python


from ...core import EUDFunc
from ...ctrlstru import (
    DoActions,
    EUDBreakIf,
    EUDElse,
    EUDEndIf,
    EUDEndInfLoop,
    EUDIf,
    EUDInfLoop,
)
from ..eudarray import EUDArray
from ..stringf.rwcommon import br1, bw1
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


@EUDFunc
def f_cp949_to_utf8_cpy(dst, src):
    # Create conversion table
    cvtb = [0] * 65536
    for (ch1, ch2), tab in cp949_table:
        cvtb[ch1 + ch2 * 256] = tab
    cvtb = EUDArray(cvtb)

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if EUDInfLoop()():
        b1 = br1.readbyte()
        EUDBreakIf(b1 == 0)
        if EUDIf()(b1 < 128):
            dst += 1
            bw1.writebyte(b1)
        if EUDElse()():
            b2 = br1.readbyte()
            EUDBreakIf(b2 == 0)
            code = cvtb[b2 * 256 + b1]
            if EUDIf()(code <= 0x07FF):
                # Encode as 2-byte
                b1 = code // (1 << 6)
                b2 = code & 0b111111
                DoActions(
                    dst.AddNumber(2),
                    b1.AddNumber(0b11000000),
                    b2.AddNumber(0b10000000),
                )
                bw1.writebyte(b1)
                bw1.writebyte(b2)
            if EUDElse()():
                # Encode as 3-byte
                b1 = code // (1 << 12)
                b2 = (code // (1 << 6)) & 0b111111
                b3 = code & 0b111111
                DoActions(
                    dst.AddNumber(3),
                    b1.AddNumber(0b11100000),
                    b2.AddNumber(0b10000000),
                    b3.AddNumber(0b10000000),
                )
                bw1.writebyte(b1)
                bw1.writebyte(b2)
                bw1.writebyte(b3)
            EUDEndIf()
        EUDEndIf()
    EUDEndInfLoop()
    bw1.writebyte(0)

    return dst
