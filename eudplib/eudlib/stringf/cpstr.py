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

from eudplib import core as c, ctrlstru as cs, utils as ut
from ..memiof import f_dwepdread_epd, f_wread_epd
from eudplib.core.curpl import _curpl_checkcond, _curpl_var


chkt = c.GetChkTokenized()


@c.EUDFunc
def GetStringAddr(strId):
    add_STR_ptr, add_STR_epd = c.Forward(), c.Forward()
    if cs.EUDExecuteOnce()():
        STR_ptr, STR_epd = f_dwepdread_epd(ut.EPD(0x5993D4))
        cs.DoActions(
            [
                c.SetMemory(add_STR_ptr + 20, c.SetTo, STR_ptr),
                c.SetMemory(add_STR_epd + 20, c.SetTo, STR_epd),
            ]
        )
    cs.EUDEndExecuteOnce()
    r, m = c.f_div(strId, 2)
    c.RawTrigger(conditions=m.Exactly(1), actions=m.SetNumber(2))
    c.RawTrigger(actions=add_STR_epd << r.AddNumber(0))
    ret = f_wread_epd(r, m)
    c.RawTrigger(actions=add_STR_ptr << ret.AddNumber(0))
    c.EUDReturn(ret)


GetMapStringAddr = GetStringAddr


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


def _s2b(x):
    if isinstance(x, str):
        x = ut.u2utf8(x)
    if isinstance(x, bytes):
        x = x + b"\r" * (-(-len(x) // 4) * 4 - len(x))
    return x


def _addcpcache(p):
    p = c.EncodePlayer(p)
    return [_curpl_var.AddNumber(p), c.SetMemory(_curpl_checkcond + 8, c.Add, p)]


class CPString:
    """
    store String in SetDeaths Actions, easy to concatenate.
    """

    def __init__(self, content=None):
        """Constructor for CPString
        :param content: Initial CPString content / capacity. Capacity of
            CPString is determined by size of this. If content is integer, then
            initial capacity and content of CPString will be set to
            content(int) and empty string.
        :type content: str, bytes, int
        """
        if isinstance(content, int):
            self.content = b"\r" * -(-content // 4) * 4
        elif isinstance(content, str) or isinstance(content, bytes):
            self.content = _s2b(content)
        else:
            raise ut.EPError("Unexpected type for CPString: %s" % type(content))

        self.length = len(self.content) // 4
        self.trigger = list()
        self.valueAddr = [0 for _ in range(self.length)]
        actions = [
            [
                c.SetDeaths(
                    c.CurrentPlayer, c.SetTo, ut.b2i4(self.content[i : i + 4]), i // 48
                )
                for i in range(4 * mod, len(self.content), 48)
            ]
            for mod in range(12)
        ]
        modlength = self.length
        addr = 0
        for i, a in enumerate(actions):
            for k in range(len(a)):
                self.valueAddr[i + 12 * k] = addr
                addr += 1
            if a and i < 11:
                a.append(c.SetMemory(0x6509B0, c.Add, 1))
                addr += 1
                modlength -= 1
        actions.extend(
            [
                [c.SetMemory(0x6509B0, c.Add, modlength) if modlength else []],
                _addcpcache(self.length),
            ]
        )
        actions = ut.FlattenList(actions)
        c.PushTriggerScope()
        for i in range(0, len(actions), 64):
            t = c.RawTrigger(actions=actions[i : i + 64])
            self.trigger.append(t)
        c.PopTriggerScope()

        self.valueAddr = [
            self.trigger[v // 64] + 348 + 32 * (v % 64) for v in self.valueAddr
        ]
        _nextptr = c.Forward()
        self.trigger[-1]._nextptr = _nextptr
        _nextptr << c.NextTrigger()

    def Display(self, action=[]):
        _next = c.Forward()
        c.RawTrigger(
            nextptr=self.trigger[0],
            actions=[action] + [c.SetNextPtr(self.trigger[-1], _next)],
        )
        _next << c.NextTrigger()

    def GetVTable(self):
        return self.trigger[0]

    def GetNextPtrMemory(self):
        return self.trigger[-1] + 4
