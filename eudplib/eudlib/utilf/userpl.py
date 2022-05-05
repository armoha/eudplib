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

from eudplib import core as c, utils as ut, ctrlstru as cs
from ..memiof import f_dwread_epd

_localcp = None
_isusercpcons = set()


def f_getuserplayerid():
    global _localcp
    if _localcp is None:
        if cs.EUDExecuteOnce()():
            _localcp = f_dwread_epd(ut.EPD(0x512684))
        cs.EUDEndExecuteOnce()
    return _localcp


def IsUserCP():
    fw = c.Forward()
    ret = c.Memory(0x6509B0, c.Exactly, fw)
    fw << IsUserCP_FW(ret)
    return ret


class IsUserCP_FW(c.ConstExpr):
    def __init__(self, condition):
        super().__init__(self)
        self._condition = condition

    def Evaluate(self):
        _RegisterIsUserCP(self._condition)
        return c.toRlocInt(0)


def RCPC_ResetConditionSet():
    _isusercpcons.clear()


c.RegisterCreatePayloadCallback(RCPC_ResetConditionSet)


def _RegisterIsUserCP(isusercp):
    _isusercpcons.add(isusercp)


class UserCPBuffer(c.EUDObject):
    def __init__(self):
        super().__init__()

    def GetDataSize(self):
        return (len(_isusercpcons) + 1) * 4

    def WritePayload(self, pbuf):
        for con in _isusercpcons:
            pbuf.WriteDword(ut.EPD(con + 8))
        pbuf.WriteDword(0xFFFFFFFF)


def _f_initisusercp():
    """(internal) Initialize IsUserCP."""
    rb = UserCPBuffer()
    ptr = c.EUDVariable(ut.EPD(rb))
    userp = f_getuserplayerid()
    write = c.Forward()
    c.VProc(userp, userp.SetDest(ut.EPD(write) + 5))

    if cs.EUDInfLoop()():
        f_dwread_epd(ptr, ret=[ut.EPD(write) + 4])
        cs.EUDBreakIf(c.Memory(write + 16, Exactly, 0xFFFFFFFF))
        c.RawTrigger(actions=[write << c.SetDeaths(0, c.SetTo, 0, 0), ptr.AddNumber(1)])

    cs.EUDEndInfLoop()
