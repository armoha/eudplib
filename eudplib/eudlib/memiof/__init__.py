#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from .bwepdio import (
    f_bread_epd,
    f_bwrite_epd,
    f_maskwrite_epd,
    f_wread_epd,
    f_wwrite_epd,
)
from .byterw import EUDByteReader, EUDByteStream, EUDByteWriter
from .cpbyterw import CPByteWriter
from .cpmemio import (
    f_bread_cp,
    f_bwrite_cp,
    f_dwadd_cp,
    f_dwepdread_cp,
    f_dwread_cp,
    f_dwsubtract_cp,
    f_dwwrite_cp,
    f_epdread_cp,
    f_maskwrite_cp,
    f_wread_cp,
    f_wwrite_cp,
)
from .dwepdio import (
    f_dwadd_epd,
    f_dwbreak,
    f_dwbreak2,
    f_dwepdread_epd,
    f_dwepdread_epd_safe,
    f_dwread_epd,
    f_dwread_epd_safe,
    f_dwsubtract_epd,
    f_dwwrite_epd,
    f_epdread_epd,
    f_epdread_epd_safe,
    f_flagread_epd,
)
from .mblockio import f_memcmp, f_memcpy, f_repmovsd_epd
from .memifgen import (
    f_cunitepdread_cp,
    f_cunitepdread_epd,
    f_cunitread_cp,
    f_cunitread_epd,
    f_epdcunitread_cp,
    f_epdcunitread_epd,
    f_epdspriteread_cp,
    f_epdspriteread_epd,
    f_maskread_cp,
    f_maskread_epd,
    f_posread_cp,
    f_posread_epd,
    f_readgen_cp,
    f_readgen_epd,
    f_spriteepdread_cp,
    f_spriteepdread_epd,
    f_spriteread_cp,
    f_spriteread_epd,
)
from .modcurpl import f_addcurpl, f_getcurpl, f_setcurpl, f_setcurpl2cpcache
from .ptrmemio import f_bread, f_bwrite, f_dwread, f_dwwrite, f_wread, f_wwrite
from .varrayreader import EUDVArrayReader
