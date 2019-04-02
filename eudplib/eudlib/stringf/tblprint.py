#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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

from ... import core as c, ctrlstru as cs, utils as ut
from ..memiof import f_dwepdread_epd
from .eudprint import f_dbstr_print


@c.EUDFunc
def GetTBLAddr(tblId):
    add_TBL_ptr, add_TBL_epd = c.Forward(), c.Forward()
    if cs.EUDExecuteOnce()():
        TBL_ptr, TBL_epd = f_dwepdread_epd(ut.EPD(0x6D5A30))
        cs.DoActions(
            [
                c.SetMemory(add_TBL_ptr + 20, c.SetTo, TBL_ptr),
                c.SetMemory(add_TBL_epd + 20, c.SetTo, TBL_epd),
            ]
        )
    cs.EUDEndExecuteOnce()
    r, m = c.f_div(tblId, 2)
    c.RawTrigger(conditions=m.Exactly(1), actions=m.SetNumber(2))
    c.RawTrigger(actions=add_TBL_epd << r.AddNumber(0))
    ret = f_wread_epd(r, m)
    c.RawTrigger(actions=add_TBL_ptr << ret.AddNumber(0))
    c.EUDReturn(ret)


def f_settbl(tblID, offset, *args):
    dst = GetTBLAddr(tblID) + offset
    f_dbstr_print(dst, *args, encoding="cp949")
