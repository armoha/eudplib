#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...core.eudfunc import EUDFullFunc
from ...core.mapdata.stringmap import ForceAddString
from ...localize import _
from ..memiof import f_getcurpl, f_setcurpl
from ..utilf import IsUserCP, f_getuserplayerid
from .cpprint import FixedText, f_cpstr_print, f_gettextptr
from .cpstr import GetMapStringAddr
from .fmtprint import _format_args
from .strfunc import f_strlen_epd
from .texteffect import (
    TextFX_FadeIn,
    TextFX_FadeOut,
    TextFX_Remove,
    get_textfx_timer,
)

_display_text = c.DisplayText(0)


@EUDFullFunc(
    [
        (ut.EPD(0x640B58), c.Add, 0, None),
        (ut.EPD(_display_text) + 1, c.SetTo, 0, None),
    ],
    [None, c.TrgString],
)
def DisplayTextAt(line, text):  # noqa: N802
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


class StringBuffer(c.EUDStruct):
    """Object for storing single modifiable string.

    Manipulating STR section is easy. :)
    You can do anything you would do with normal string with StringBuffer.
    """

    _fields_ = (
        ("StringIndex", c.TrgString),  # static
        "epd",  # static
        "pos",
        "capacity",  # static
    )

    _method_template = c.Forward()
    _cpbranch = c.Forward()

    def __init__(self, content=None, *, _from=None):
        """Constructor for StringBuffer

        :param content: Initial StringBuffer content / capacity. Capacity of
            StringBuffer is determined by size of this. If content is integer,
            then initial capacity and content of StringBuffer will be set to
            content(int) and empty string.

        :type content: str, bytes, int
        """
        if _from is None or (
            isinstance(_from, StringBuffer) and c.IsConstExpr(_from)
        ):
            if _from is None:
                if content is None:
                    content = "\r" * 218
                elif isinstance(content, int):
                    content = "\r" * content
                else:
                    content = ut.u2utf8(content)

                string_id = ForceAddString(content)
                epd = ut.EPD(GetMapStringAddr(string_id))
                capacity = len(content)
                super().__init__(
                    _from=None, _static_initval=[string_id, epd, 0, capacity]
                )
            else:
                string_id = _from._StringIndex
                epd = _from._epd
                capacity = _from._capacity
                super().__init__(_from=_from)

            # static fields
            object.__setattr__(self, "_initialized", False)
            self._StringIndex = string_id
            self._epd = epd
            self._capacity = capacity
            self._initialized = True

        else:
            super().__init__(_from=_from)

    def constructor(self, *args, **kwargs):
        raise ut.EPError(_("Dynamically allocating StringBuffer is not supported"))

    def constructor_static(self, *args, **kwargs):
        pass

    @classmethod
    def alloc(cls, *args, **kwargs):
        raise ut.EPError(_("Dynamically allocating StringBuffer is not supported"))

    @classmethod
    def free(cls, data):
        raise ut.EPError(_("Dynamically allocating StringBuffer is not supported"))

    def destructor(self):
        raise ut.EPError(_("Dynamically allocating StringBuffer is not supported"))

    # Initializer

    def setall(self, values):
        raise ut.EPError(_("Can't mutate field of StringBuffer except 'pos'"))

    def copyto(self, inst):
        raise ut.EPError(_("Can't clone StringBuffer, which is reference type."))

    # Field setter & getter

    def getfield(self, name):
        # get static field
        if c.IsConstExpr(self.getValue()) and name != "pos":
            return getattr(self, f"_{name}")
        return super().getfield(name)

    def setfield(self, name, value):
        ut.ep_assert(
            name == "pos", _("Can't mutate field of StringBuffer except 'pos'")
        )
        super().setfield(name, value)

    def iaddattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().iaddattr(name, value)

    def isubtractattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().isubtractattr(name, value)

    def isubattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().isubattr(name, value)

    def imulattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().imulattr(name, value)

    def ifloordivattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().ifloordivattr(name, value)

    def imodattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().imodattr(name, value)

    def ilshiftattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().ilshiftattr(name, value)

    def irshiftattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().irshiftattr(name, value)

    def ipowattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().ipowattr(name, value)

    def iandattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().iandattr(name, value)

    def iorattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().iorattr(name, value)

    def ixorattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().ixorattr(name, value)

    def iinvertattr(self, name, value):
        if name != "pos":
            raise AttributeError
        super().iinvertattr(name, value)

    @classmethod
    def _init_template(cls):
        c.PushTriggerScope()
        cls._method_template << c.NextTrigger()
        _localcp = f_getuserplayerid()
        cls._cpbranch << c.RawTrigger(
            conditions=IsUserCP(), actions=c.SetNextPtr(cls._cpbranch, 0)
        )
        c.PopTriggerScope()

    @classmethod
    def _cpblock(cls):
        if not cls._method_template.IsSet():
            cls._init_template()
        end, ontrue = c.Forward(), c.Forward()
        c.RawTrigger(
            nextptr=cls._method_template,
            actions=[
                c.SetNextPtr(cls._cpbranch, end),
                c.SetMemory(cls._cpbranch + 348, c.SetTo, ontrue),
            ],
        )
        ontrue << c.NextTrigger()
        yield end
        end << c.NextTrigger()

    def append(self, *args):
        for _end in self._cpblock():
            f_setcurpl(self.pos)
            f_cpstr_print(*args)
            self.pos = f_getcurpl()
            f_setcurpl(f_getuserplayerid())

    def appendf(self, format_string, *args):
        self.append(*_format_args(format_string, *args))

    def insert(self, index, *args):
        for _end in self._cpblock():
            f_setcurpl(self.epd + index)
            f_cpstr_print(*args, EOS=False)
            self.pos = f_getcurpl()
            f_setcurpl(f_getuserplayerid())

    def insertf(self, index, format_string, *args):
        self.insert(index, *_format_args(format_string, *args))

    def delete(self, start, length=1):
        for _end in self._cpblock():
            pos = self.epd + start
            self.pos = pos
            f_setcurpl(pos)
            cs.DoActions(
                [
                    c.SetDeaths(c.CurrentPlayer, c.SetTo, 0x0D0D0D0D, 0),
                    c.AddCurrentPlayer(1),
                ]
                for _ in range(length)
            )
            f_setcurpl(f_getuserplayerid())

    def Display(self):  # noqa: N802
        cs.DoActions(c.DisplayText(self.StringIndex))

    def DisplayAt(self, line, _f={}):  # noqa: N802
        for _end in self._cpblock():
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
        for _end in self._cpblock():
            f_setcurpl(self.epd)
            f_cpstr_print(*args, EOS=False)
            cs.DoActions(
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
                *c.SetCurrentPlayer(f_getuserplayerid()),
                c.DisplayText(self.StringIndex),
            )

    def printf(self, format_string, *args):
        self.print(*_format_args(format_string, *args))

    def printAt(self, line, *args):  # noqa: N802
        if len(args) == 1 and isinstance(args[0], str):
            return DisplayTextAt(line, args[0])
        for _end in self._cpblock():
            f_setcurpl(self.epd)
            f_cpstr_print(*args, EOS=False)
            cs.DoActions(
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
                *c.SetCurrentPlayer(f_getuserplayerid()),
            )
            self.DisplayAt(line)

    def printfAt(self, line, format_string, *args):  # noqa: N802
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
        if not self._method_template.IsSet():
            self._init_template()
        end, ontrue = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        c.RawTrigger(
            nextptr=self._method_template,
            actions=[
                c.SetNextPtr(self._cpbranch, end),
                c.SetMemory(self._cpbranch + 348, c.SetTo, ontrue),
                ret.SetNumber(-1),
            ],
        )
        ontrue << c.NextTrigger()
        prevpos = TextFX_Remove(tag)
        f_setcurpl(self.epd)
        _, _, identifier = get_textfx_timer(tag)
        _tag_print(identifier, *fmtargs)
        self._display_at(prevpos, line)
        end << c.NextTrigger()

    def Play(self):  # noqa: N802
        cs.DoActions(c.PlayWAV(self.StringIndex))

    def fadeIn(self, *args, color=None, wait=1, reset=True, line=-1, tag=None):  # noqa: N802
        if tag is None:
            if len(args) == 1:
                tag = args[0]
            else:
                tag = args
        if not self._method_template.IsSet():
            self._init_template()
        end, ontrue = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        c.RawTrigger(
            nextptr=self._method_template,
            actions=[
                c.SetNextPtr(self._cpbranch, end),
                c.SetMemory(self._cpbranch + 348, c.SetTo, ontrue),
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

    def fadeInf(  # noqa: N802
        self,
        format_string,
        *args,
        color=None,
        wait=1,
        reset=True,
        line=-1,
        tag=None,
    ):
        fmtargs = _format_args(format_string, *args)
        return self.fadeIn(
            *fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag
        )

    def fadeOut(  # noqa: N802
        self, *args, color=None, wait=1, reset=True, line=-1, tag=None
    ):
        if tag is None:
            if len(args) == 1:
                tag = args[0]
            else:
                tag = args
        if not self._method_template.IsSet():
            self._init_template()
        end, ontrue = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        c.RawTrigger(
            nextptr=self._method_template,
            actions=[
                c.SetNextPtr(self._cpbranch, end),
                c.SetMemory(self._cpbranch + 348, c.SetTo, ontrue),
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

    def fadeOutf(  # noqa: N802
        self,
        format_string,
        *args,
        color=None,
        wait=1,
        reset=True,
        line=-1,
        tag=None,
    ):
        fmtargs = _format_args(format_string, *args)
        return self.fadeOut(
            *fmtargs, color=color, wait=wait, reset=reset, line=line, tag=tag
        )

    def length(self):
        return f_strlen_epd(self.epd)


_globalsb = None


def GetGlobalStringBuffer():  # noqa: N802
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


def f_printAt(line, format_string, *args):  # noqa: N802
    gsb = GetGlobalStringBuffer()
    gsb.printfAt(line, format_string, *args)
