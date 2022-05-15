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


from .allocator import Forward
from .variable import EUDVariable
from .rawtrigger import EncodePlayer, Memory, SetMemory, SetTo, Add, Exactly
from ..utils import EPD


_curpl_var = EUDVariable(EPD(0x6509B0), SetTo, 0)
_curpl_checkcond = Forward()


def cpcacheMatchCond():
    if not _curpl_checkcond.IsSet():
        _curpl_checkcond << Memory(0x6509B0, Exactly, 0)
    return _curpl_checkcond


def SetCurrentPlayer(p):
    p = EncodePlayer(p)
    return [
        _curpl_var.SetNumber(p),
        SetMemory(_curpl_checkcond + 8, SetTo, p),
        SetMemory(0x6509B0, SetTo, p),
    ]


def AddCurrentPlayer(p):
    p = EncodePlayer(p)
    return [
        _curpl_var.AddNumber(p),
        SetMemory(_curpl_checkcond + 8, Add, p),
        SetMemory(0x6509B0, Add, p),
    ]


def GetCPCache():
    return _curpl_var
