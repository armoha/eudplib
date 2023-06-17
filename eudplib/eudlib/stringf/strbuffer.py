#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...core.mapdata.stringmap import ForceAddString
from ..eudarray import EUDArray
from ..memiof import f_getcurpl, f_setcurpl
from ..utilf import IsUserCP, f_getuserplayerid
from .cpprint import FixedText, f_cpstr_print, f_gettextptr
from .cpstr import GetMapStringAddr
from .fmtprint import _format_args
from .strfunc import f_strlen_epd
from .texteffect import TextFX_FadeIn, TextFX_FadeOut, TextFX_Remove, _get_TextFX_timer

_display_text = c.DisplayText(0)


@c.EUDFullFunc(
    [(ut.EPD(0x640B58), c.Add, 0, None), (ut.EPD(_display_text) + 1, c.SetTo, 0, None)],
    [None, c.TrgString],
)
def DisplayTextAt(line, text):
    with FixedText(_display_text):
        c.VProc([line, text], [])
        c.RawTrigger(
            conditions=c.Memory(0x640B58, c.AtLeast, 11),
            actions=c.SetMemory(0x640B58, c.Subtract, 11),
        )


def _tag_print(identifier, *args, encoding="UTF-8"):
    args = ut.FlattenList(args)
    ut.ep_assert(len(args) > 0, "No text provided for tagprint")

    try:
        args[0] = identifier + args[0]
    except TypeError:
        try:
            args[0] = identifier.decode("ascii") + args[0]
        except TypeError:
            args.insert(0, identifier)

    for arg in args:
        if isinstance(arg, bytes):
            arg = arg.decode(encoding)
        if isinstance(arg, str) and "\n" in arg:
            new_arg = arg.split("\n")[0]
            for line in arg.split("\n")[1:]:
                if line == "":
                    new_arg += "\n"
                else:
                    new_arg += "\n" + identifier.decode("ascii") + line
            f_cpstr_print(new_arg, EOS=False, encoding=encoding)
        else:
            f_cpstr_print(arg, EOS=False, encoding=encoding)

    cs.DoActions(c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0))


class StringBuffer:
    """Object for storing single modifiable string.

    Manipulating STR section is easy. :)
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
        _chkt = c.GetChkTokenized()
        if content is None:
            content = "\r" * 218
        elif isinstance(content, int):
            content = "\r" * content
        else:
            content = ut.u2utf8(content)
        self.capacity = len(content)
        self.StringIndex = ForceAddString(content)
        self.epd = ut.EPD(GetMapStringAddr(self.StringIndex))
        self.pos = c.EUDVariable()

    @classmethod
    def _init_template(cls):
        c.PushTriggerScope()
        cls._method_template << c.NextTrigger()
        _localcp = f_getuserplayerid()
        cls._cpbranch << c.RawTrigger(
            conditions=IsUserCP(),
            actions=c.SetNextPtr(cls._cpbranch, 0),
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
        ontrue << c.NextTrigger()
        yield end
        end << c.NextTrigger()

    def append(self, *args):
        for _end in StringBuffer.CPBranch():
            f_setcurpl(self.pos)
            f_cpstr_print(*args)
            f_getcurpl(ret=[self.pos])
            f_setcurpl(f_getuserplayerid())

    def appendf(self, format_string, *args):
        self.append(*_format_args(format_string, *args))

    def insert(self, index, *args):
        for _end in StringBuffer.CPBranch():
            f_setcurpl(self.epd + index)
            f_cpstr_print(*args, EOS=False)
            f_getcurpl(ret=[self.pos])
            f_setcurpl(f_getuserplayerid())

    def insertf(self, index, format_string, *args):
        self.insert(index, *_format_args(format_string, *args))

    def delete(self, start, length=1):
        for _end in StringBuffer.CPBranch():
            self.pos << self.epd + start
            f_setcurpl(self.pos)
            cs.DoActions(
                [
                    c.SetDeaths(c.CurrentPlayer, c.SetTo, 0x0D0D0D0D, 0),
                    c.AddCurrentPlayer(1),
                ]
                for _ in range(length)
            )
            f_setcurpl(f_getuserplayerid())

    def Display(self):
        cs.DoActions(c.DisplayText(self.StringIndex))

    def DisplayAt(self, line, _f={}):
        for _end in StringBuffer.CPBranch():
            with FixedText(c.DisplayText(self.StringIndex)):
                if c.IsEUDVariable(line):
                    c.VProc(line, line.QueueAddTo(ut.EPD(0x640B58)))
                elif not isinstance(line, int) or line != 0:
                    cs.DoActions(c.SetMemory(0x640B58, c.Add, line))
                if not isinstance(line, int) or line != 0:
                    c.RawTrigger(
                        conditions=c.Memory(0x640B58, c.AtLeast, 11),
                        actions=c.SetMemory(0x640B58, c.Subtract, 11),
                    )

    def print(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            return cs.DoActions(c.DisplayText(args[0]))
        for _end in StringBuffer.CPBranch():
            f_setcurpl(self.epd)
            f_cpstr_print(*args, EOS=False)
            cs.DoActions(
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
                c.SetCurrentPlayer(f_getuserplayerid()),
                c.DisplayText(self.StringIndex),
            )

    def printf(self, format_string, *args):
        self.print(*_format_args(format_string, *args))

    def printAt(self, line, *args):
        if len(args) == 1 and isinstance(args[0], str):
            return DisplayTextAt(line, args[0])
        for _end in StringBuffer.CPBranch():
            f_setcurpl(self.epd)
            f_cpstr_print(*args, EOS=False)
            cs.DoActions(
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
                c.SetCurrentPlayer(f_getuserplayerid()),
            )
            self.DisplayAt(line)

    def printfAt(self, line, format_string, *args):
        self.printAt(line, *_format_args(format_string, *args))

    def _display_at(self, prevpos, line):
        f_setcurpl(f_getuserplayerid())
        if isinstance(line, int):
            if line == 10:
                prevptr = f_gettextptr()
                prevptr -= 1
                if cs.EUDIf()(prevpos == prevptr):
                    self.DisplayAt(10)
                if cs.EUDElse()():
                    self.Display()
                cs.EUDEndIf()
            elif 0 <= line < 10:
                self.DisplayAt(line)
            elif line >= -11:
                if cs.EUDIf()(prevpos == -1):
                    if line == -1:
                        self.Display()
                    else:
                        self.DisplayAt(11 + line)
                if cs.EUDElse()():
                    with FixedText(c.DisplayText(self.StringIndex)):
                        c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                cs.EUDEndIf()
        else:
            if cs.EUDIf()(line == 10):
                prevptr = f_gettextptr()
                prevptr -= 1
                if cs.EUDIf()(prevpos == prevptr):
                    self.DisplayAt(10)
                if cs.EUDElse()():
                    self.Display()
                cs.EUDEndIf()
            if cs.EUDElseIf()(line < 10):
                self.DisplayAt(line)
            if cs.EUDElseIf()(line >= 0xFFFFFFF5):
                if cs.EUDIf()(prevpos == -1):
                    if cs.EUDIf()(line == -1):
                        self.Display()
                    if cs.EUDElse()():
                        self.DisplayAt(11 + line)
                    cs.EUDEndIf()
                if cs.EUDElse()():
                    with FixedText(c.DisplayText(self.StringIndex)):
                        c.VProc(prevpos, prevpos.SetDest(ut.EPD(0x640B58)))
                cs.EUDEndIf()
            cs.EUDEndIf()

    def tagprint(self, format_string, *args, line=-1, tag=None):
        fmtargs = _format_args(format_string, *args)
        if tag is None:
            if len(fmtargs) == 1:
                tag = fmtargs[0]
            else:
                tag = fmtargs
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
        _, _, identifier = _get_TextFX_timer(tag)
        _tag_print(identifier, *fmtargs)
        self._display_at(prevpos, line)
        end << c.NextTrigger()

    def Play(self):
        cs.DoActions(c.PlayWAV(self.StringIndex))

    def fadeIn(self, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        if tag is None:
            if len(args) == 1:
                tag = args[0]
            else:
                tag = args
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
        self._display_at(prevpos, line)
        end << c.NextTrigger()
        return ret

    def fadeInf(self, format_string, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        fmtargs = _format_args(format_string, *args)
        return self.fadeIn(*fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag)

    def fadeOut(self, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        if tag is None:
            if len(args) == 1:
                tag = args[0]
            else:
                tag = args
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
        self._display_at(prevpos, line)
        end << c.NextTrigger()
        return ret

    def fadeOutf(self, format_string, *args, color=None, wait=1, reset=True, line=-1, tag=None):
        fmtargs = _format_args(format_string, *args)
        return self.fadeOut(*fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag)

    def length(self):
        return f_strlen_epd(self.epd)


_globalsb = None


def GetGlobalStringBuffer():
    global _globalsb
    if _globalsb is None:
        _globalsb = StringBuffer(1023)
    return _globalsb


# FIXME: Optimize these functions to cache string contents
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
