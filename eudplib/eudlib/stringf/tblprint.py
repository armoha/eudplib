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
from ..memiof import f_dwepdread_epd, f_wread_epd
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
    from .eudprint import hptr, _str_jump, _str_EOS, _str_dst, _dw_jump, _dw_EOS, _dw_dst, _ptr_jump, _ptr_EOS, _ptr_dst
    dst = GetTBLAddr(tblID) + offset
    dw = any(c.IsConstExpr(x) or c.IsEUDVariable(x) for x in args)
    ptr = any(ut.isUnproxyInstance(x, hptr) for x in args)
    cs.DoActions([c.SetNextPtr(_str_jump, _str_dst)] +
    [
        c.SetNextPtr(_dw_jump, _dw_dst)
        if dw else []
    ] + [
        c.SetNextPtr(_ptr_jump, _ptr_dst)
        if ptr else []
    ])
    f_dbstr_print(dst, *args, encoding="cp949")
    cs.DoActions([c.SetNextPtr(_str_jump, _str_EOS)] +
    [
        c.SetNextPtr(_dw_jump, _dw_EOS)
        if dw else []
    ] + [
        c.SetNextPtr(_ptr_jump, _ptr_EOS)
        if ptr else []
    ])
