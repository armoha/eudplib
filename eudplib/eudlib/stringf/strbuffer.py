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

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...core.mapdata.stringmap import (
    ForceAddString,
    ApplyStringMap,
    GetStringMap,
)
from ..eudarray import EUDArray
from ..memiof import f_dwread_epd, f_getcurpl, f_setcurpl, f_wread_epd
from ..utilf import f_getuserplayerid, IsUserCP
from .cpprint import f_cpstr_print, f_gettextptr
from .cpstr import GetMapStringAddr
from .fmtprint import _format_args
from .strfunc import f_strlen_epd
from .texteffect import TextFX_FadeIn, TextFX_FadeOut, TextFX_Remove


@c.EUDTypedFunc([None, c.TrgString])
def DisplayTextAt(line, text):
    tp = f_gettextptr()
    c.VProc(line, line.QueueAddTo(ut.EPD(0x640B58)))
    c.RawTrigger(
        conditions=c.Memory(0x640B58, c.AtLeast, 11),
        actions=c.SetMemory(0x640B58, c.Subtract, 11),
    )
    cs.DoActions(c.DisplayText(text), c.SetMemory(0x640B58, c.SetTo, tp))


class StringBuffer:
    """Object for storing single modifiable string.

    Manipluating STR section is easy. :)
    You can do anything you would do with normal string with StringBuffer.
    """

    _method_template = c.Forward()
    _cpbranch = c.Forward()

    def __init__(self, content=None):
        """Constructor for StringBuffer

        :param content: Initial StringBuffer content / capacity. Capacity of
            StringBuffer is determined by size of this. If content is integer, then
            initial capacity and content of StringBuffer will be set to
            content(int) and empty string.

        :type content: str, bytes, int
        """
        chkt = c.GetChkTokenized()
        if content is None:
            content = "\r" * 218
        elif isinstance(content, int):
            content = "\r" * content
        else:
            content = ut.u2utf8(content)
        self.capacity = len(content)
        self.StringIndex = ForceAddString(content)
        self.epd, self.pos = c.EUDVariable(), c.EUDVariable()

        try:
            cs.EUDExecuteOnce()()
            cs.DoActions(self.epd.SetNumber(ut.EPD(GetMapStringAddr(self.StringIndex))))
            cs.EUDEndExecuteOnce()
        except IndexError:
            from ...maprw.injector.mainloop import EUDOnStart

            def _f():
                cs.DoActions(
                    self.epd.SetNumber(ut.EPD(GetMapStringAddr(self.StringIndex)))
                )

            EUDOnStart(_f)

    @classmethod
    def _init_template(cls):
        c.PushTriggerScope()
        cls._method_template << c.NextTrigger()
        localcp = f_getuserplayerid()
        cls._cpbranch << c.RawTrigger(
            nextptr=0, conditions=IsUserCP(), actions=c.SetNextPtr(cls._cpbranch, 0),
        )
        c.PopTriggerScope()

    @classmethod
    def CPBranch(cls):
        if not StringBuffer._method_template.IsSet():
            StringBuffer._init_template()
        end, ontrue = c.Forward(), c.Forward()
        c.RawTrigger(
            nextptr=StringBuffer._method_template,
            actions=[
                c.SetNextPtr(StringBuffer._cpbranch, end),
                c.SetMemory(StringBuffer._cpbranch + 348, c.SetTo, ontrue),
            ],
        )
        return end, ontrue

    def append(self, *args):
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        f_setcurpl(self.pos)
        f_cpstr_print(*args)
        f_getcurpl(ret=[self.pos])
        f_setcurpl(f_getuserplayerid())
        end << c.NextTrigger()

    def appendf(self, format_string, *args):
        fmtargs = _format_args(format_string, *args)
        self.append(*fmtargs)

    def insert(self, index, *args):
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        f_setcurpl(self.epd + index)
        f_cpstr_print(*args, EOS=False)
        f_getcurpl(ret=[self.pos])
        f_setcurpl(f_getuserplayerid())
        end << c.NextTrigger()

    def insertf(self, index, format_string, *args):
        fmtargs = _format_args(format_string, *args)
        self.insert(index, *fmtargs)

    def delete(self, start, length=1):
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        self.pos << self.epd
        self.pos += start
        f_setcurpl(self.pos)
        cs.DoActions(
            [
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0x0D0D0D0D, 0),
                c.AddCurrentPlayer(1),
            ]
            for _ in range(length)
        )
        f_setcurpl(f_getuserplayerid())
        end << c.NextTrigger()

    def Display(self):
        cs.DoActions(c.DisplayText(self.StringIndex))

    def DisplayAt(self, line):
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        prevptr = f_gettextptr()
        cs.DoActions(c.SetMemory(0x640B58, c.Add, line))
        c.RawTrigger(
            conditions=c.Memory(0x640B58, c.AtLeast, 11),
            actions=c.SetMemory(0x640B58, c.Subtract, 11),
        )
        c.VProc(
            prevptr,
            [c.DisplayText(self.StringIndex), prevptr.SetDest(ut.EPD(0x640B58))],
        )
        end << c.NextTrigger()

    def print(self, *args):
        if len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 31:
            cs.DoActions(c.DisplayText(args[0]))
            return
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        f_setcurpl(self.epd)
        f_cpstr_print(*args, EOS=False)
        cs.DoActions(
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetCurrentPlayer(f_getuserplayerid()),
            c.DisplayText(self.StringIndex),
        )
        end << c.NextTrigger()

    def printf(self, format_string, *args):
        fmtargs = _format_args(format_string, *args)
        self.print(*fmtargs)

    def printAt(self, line, *args):
        end, ontrue = StringBuffer.CPBranch()
        ontrue << c.NextTrigger()
        f_setcurpl(self.epd)
        f_cpstr_print(*args, EOS=False)
        cs.DoActions(
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetCurrentPlayer(f_getuserplayerid()),
        )
        self.DisplayAt(line)
        end << c.NextTrigger()

    def printfAt(self, line, format_string, *args):
        fmtargs = _format_args(format_string, *args)
        self.printAt(line, *fmtargs)

    def Play(self):
        cs.DoActions(c.PlayWAV(self.StringIndex))

    def fadeIn(self, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        if not StringBuffer._method_template.IsSet():
            StringBuffer._init_template()
        end, ontrue = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        c.RawTrigger(
            nextptr=StringBuffer._method_template,
            actions=[
                c.SetNextPtr(StringBuffer._cpbranch, end),
                c.SetMemory(StringBuffer._cpbranch + 348, c.SetTo, ontrue),
                ret.SetNumber(-1),
            ],
        )
        ontrue << c.NextTrigger()
        prevpos = TextFX_Remove(tag)
        f_setcurpl(self.epd)
        ret << TextFX_FadeIn(*args, color=color, wait=wait, reset=reset, tag=tag)
        f_setcurpl(f_getuserplayerid())
        if type(line) == int:
            if 0 <= line <= 10:
                self.DisplayAt(line)
            elif line >= -11:
                if cs.EUDIf()(prevpos == -1):
                    self.DisplayAt(11 + line)
                if cs.EUDElse()():
                    prevptr = f_gettextptr()
                    c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                    c.VProc(
                        prevptr,
                        [
                            c.DisplayText(self.StringIndex),
                            prevptr.SetDest(ut.EPD(0x640B58)),
                        ],
                    )
                cs.EUDEndIf()
        else:
            if cs.EUDIf()(line <= 10):
                self.DisplayAt(line)
            if cs.EUDElseIf()(line >= 0xFFFFFFF5):
                if cs.EUDIf()(prevpos == -1):
                    self.DisplayAt(11 + line)
                if cs.EUDElse()():
                    prevptr = f_gettextptr()
                    c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                    c.VProc(
                        prevptr,
                        [
                            c.DisplayText(self.StringIndex),
                            prevptr.SetDest(ut.EPD(0x640B58)),
                        ],
                    )
                cs.EUDEndIf()
            cs.EUDEndIf()
        end << c.NextTrigger()
        return ret

    def fadeInf(
        self, format_string, *args, color=None, wait=1, reset=True, line=-1, tag=None
    ):
        fmtargs = _format_args(format_string, *args)
        return self.fadeIn(
            *fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag
        )

    def fadeOut(self, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        if not StringBuffer._method_template.IsSet():
            StringBuffer._init_template()
        end, ontrue = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        c.RawTrigger(
            nextptr=StringBuffer._method_template,
            actions=[
                c.SetNextPtr(StringBuffer._cpbranch, end),
                c.SetMemory(StringBuffer._cpbranch + 348, c.SetTo, ontrue),
                ret.SetNumber(-1),
            ],
        )
        ontrue << c.NextTrigger()
        prevpos = TextFX_Remove(tag)
        f_setcurpl(self.epd)
        ret << TextFX_FadeOut(*args, color=color, wait=wait, reset=reset, tag=tag)
        f_setcurpl(f_getuserplayerid())
        if type(line) == int:
            if 0 <= line <= 10:
                self.DisplayAt(line)
            elif line >= -11:
                if cs.EUDIf()(prevpos == -1):
                    self.DisplayAt(11 + line)
                if cs.EUDElse()():
                    prevptr = f_gettextptr()
                    c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                    c.VProc(
                        prevptr,
                        [
                            c.DisplayText(self.StringIndex),
                            prevptr.SetDest(ut.EPD(0x640B58)),
                        ],
                    )
                cs.EUDEndIf()
        else:
            if cs.EUDIf()(line <= 10):
                self.DisplayAt(line)
            if cs.EUDElseIf()(line >= 0xFFFFFFF5):
                if cs.EUDIf()(prevpos == -1):
                    self.DisplayAt(11 + line)
                if cs.EUDElse()():
                    prevptr = f_gettextptr()
                    c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                    c.VProc(
                        prevptr,
                        [
                            c.DisplayText(self.StringIndex),
                            prevptr.SetDest(ut.EPD(0x640B58)),
                        ],
                    )
                cs.EUDEndIf()
            cs.EUDEndIf()
        end << c.NextTrigger()
        return ret

    def fadeOutf(
        self, format_string, *args, color=None, wait=1, reset=True, line=-1, tag=None
    ):
        fmtargs = _format_args(format_string, *args)
        return self.fadeOut(
            *fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag
        )

    def length(self):
        return f_strlen_epd(self.epd)


_globalsb = None


def GetGlobalStringBuffer():
    global _globalsb
    if _globalsb is None:
        _globalsb = StringBuffer(1023)
    return _globalsb


def f_simpleprint(*args, spaced=True):
    # Add spaces between arguments
    if spaced:
        spaced_args = []
        for arg in args:
            spaced_args.extend([arg, " "])
        args = spaced_args[:-1]

    # Print
    oldcp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    gsb = GetGlobalStringBuffer()
    gsb.print(*args)
    f_setcurpl(oldcp)


def f_println(format_string, *args):
    gsb = GetGlobalStringBuffer()
    gsb.printf(format_string, *args)


def f_printAt(line, format_string, *args):
    gsb = GetGlobalStringBuffer()
    gsb.printfAt(line, format_string, *args)
