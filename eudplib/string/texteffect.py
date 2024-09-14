#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import itertools

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..memio import f_getcurpl, f_setcurpl, f_setcurpl2cpcache
from ..memio.rwcommon import br1
from ..scdata.scdata import CurrentPlayer
from .cpprint import cw, f_cpstr_print
from .eudprint import epd2s, ptr2s

color_codes = list(range(1, 32))
color_codes.remove(0x9)  # tab
color_codes.remove(0xA)  # linebreak
color_codes.remove(0xC)  # linebreak
color_codes.remove(0x12)  # right align
color_codes.remove(0x13)  # center align
color_v = c.EUDVariable(2)
color_code = b"\x02"


@c.EUDFunc
def _cpchar_addstr():
    if cs.EUDInfLoop()():
        b1 = br1.readbyte()
        cs.EUDBreakIf(b1 == 0)
        cw.writebyte(color_v)
        cw.writebyte(b1)
        if cs.EUDIf()(b1 <= 0x7F):
            cw.flushdword()
        if cs.EUDElse()():
            b2 = br1.readbyte()
            cw.writebyte(b2)
            if cs.EUDIf()(b1 <= 0xDF):  # Encode as 2-byte
                cw.flushdword()
            if cs.EUDElse()():  # 3-byte
                cw.writebyte(br1.readbyte())
            cs.EUDEndIf()
        cs.EUDEndIf()
    cs.EUDEndInfLoop()


def f_cpchar_addstr(src):
    br1.seekoffset(src)
    _cpchar_addstr()


def f_cpchar_addstr_epd(src):
    br1.seekepd(src)
    _cpchar_addstr()


@c.EUDFunc
def f_cpchar_adddw(number):
    skipper = [c.Forward() for _ in range(9)]
    ch = [0] * 10

    for i in range(10):  # Get digits
        number, ch[i] = c.f_div(number, 10)
        if i != 9:
            cs.EUDJumpIf(number == 0, skipper[i])

    for i in range(9, -1, -1):  # print digits
        if i != 9:
            skipper[i] << c.NextTrigger()
        cs.DoActions(
            c.SetDeaths(
                CurrentPlayer,
                c.SetTo,
                color_v + ch[i] * 256 + (0x0D0D3000),
                0,
            ),
            c.AddCurrentPlayer(1),
        )


def f_cpchar_print(*args, EOS=True, encoding="UTF-8"):  # noqa: N803
    global color_code
    args = ut.FlattenList(args)

    if encoding.upper() == "UTF-8":
        encode_func = ut.u2utf8
    else:
        encode_func = ut.u2b

    for arg in args:
        if isinstance(arg, bytes):
            arg = arg.decode(encoding)
        if isinstance(arg, str):
            bytestring = b""
            new_color_code = color_code
            for char in arg:
                char = encode_func(char)
                if ut.b2i1(char) in color_codes:
                    new_color_code = char
                    continue
                while len(char) < 3:
                    char = char + b"\r"
                bytestring = bytestring + new_color_code + char
            if not bytestring:
                bytestring = color_code + b"\r\r\r"
            f_cpstr_print(bytestring, EOS=False)
            if color_code != new_color_code:
                color_code = new_color_code
                cs.DoActions(color_v.SetNumber(ut.b2i1(color_code)))
        elif ut.isUnproxyInstance(arg, ptr2s):
            f_cpchar_addstr(arg._value)
        elif ut.isUnproxyInstance(arg, epd2s):
            f_cpchar_addstr_epd(arg._value)
        elif c.IsEUDVariable(arg) or c.IsConstExpr(arg):
            f_cpchar_adddw(arg)
        else:
            f_cpstr_print(arg, EOS=False, encoding=encoding)
    if EOS:
        cs.DoActions(c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0))


_TextFX_dict = dict()
id_codes = [
    "\x18",
    "\x02",
    "\x03",
    "\x04",
    "\x06",
    "\x07",
    "\x08",
    "\x0D",
    "\x0E",
    "\x0F",
    "\x10",
    "\x11",
    "\x15",
    "\x16",
    "\x17",
    "\x19",
    "\x1A",
    "\x1B",
    "\x1C",
    "\x1D",
    "\x1E",
    "\x1F",
]
id_gen = itertools.cycle(itertools.product(id_codes, repeat=6))


def _add_textfx_timer(tag):
    if tag not in _TextFX_dict:
        _TextFX_dict[tag] = (
            c.EUDVariable(),
            c.EUDLightVariable(),
            ut.u2b("".join(next(id_gen))),
        )


def get_textfx_timer(tag):
    return _TextFX_dict[tag]


def TextFX_SetTimer(tag, modtype, value):  # noqa: N802
    _add_textfx_timer(tag)
    timer, _, _ = get_textfx_timer(tag)
    cs.DoActions(c.SetMemory(timer.getValueAddr(), modtype, value))


@c.EUDFunc
def _remove_textfx(o0, o1, e0, e1):
    textptr = c.EUDVariable()
    e0t, e1t, e_fail, o0t, o1t, o_fail = (c.Forward() for _ in range(6))
    setptr_o, setptr_e = c.Forward(), c.Forward()

    c.VProc(
        [o0, o1, e0, e1],
        [
            textptr.SetNumber(-1),
            c.SetMemory(0x6509B0, c.SetTo, ut.EPD(0x640B60 + 218 * 11)),
            c.SetMemory(setptr_o + 20, c.SetTo, 10),
            c.SetMemory(setptr_e + 20, c.SetTo, 11),
            o0.SetDest(ut.EPD(o0t + 16)),
            o1.SetDest(ut.EPD(o1t + 16)),
            e0.SetDest(ut.EPD(e0t + 16)),
            e1.SetDest(ut.EPD(e1t + 16)),
        ],
    )
    if cs.EUDLoopN()(6):
        incr_e, incr_o = c.Forward(), c.Forward()
        e0t << c.RawTrigger(
            nextptr=incr_e,
            conditions=c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF0000),
            actions=[c.SetMemory(0x6509B0, c.Add, 1), c.SetNextPtr(e0t, e1t)],
        )
        e1t << c.RawTrigger(
            conditions=c.Deaths(CurrentPlayer, c.Exactly, 0, 0),
            actions=[
                c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0),
                c.SetMemory(0x6509B0, c.Subtract, 1),
                c.SetDeathsX(CurrentPlayer, c.SetTo, 0, 0, 0xFFFF0000),
                setptr_e << textptr.SetNumber(0),
                c.SetNextPtr(e1t, incr_e),
            ],
        )
        e_fail << c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Subtract, 1))
        incr_e << c.RawTrigger(
            actions=[
                c.SetNextPtr(e0t, incr_e),
                c.SetNextPtr(e1t, e_fail),
                c.SetMemory(0x6509B0, c.Subtract, 216 // 4),
                c.SetMemory(setptr_e + 20, c.Subtract, 2),
            ]
        )
        o0t << c.RawTrigger(
            nextptr=incr_o,
            conditions=c.Deaths(CurrentPlayer, c.Exactly, 0, 0),
            actions=[c.SetMemory(0x6509B0, c.Add, 1), c.SetNextPtr(o0t, o1t)],
        )
        o1t << c.RawTrigger(
            conditions=c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF),
            actions=[
                c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0),
                c.SetMemory(0x6509B0, c.Subtract, 1),
                c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0),
                setptr_o << textptr.SetNumber(0),
                c.SetNextPtr(o1t, incr_o),
            ],
        )
        o_fail << c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Subtract, 1))
        incr_o << c.RawTrigger(
            actions=[
                c.SetNextPtr(o0t, incr_o),
                c.SetNextPtr(o1t, o_fail),
                c.SetMemory(0x6509B0, c.Subtract, 220 // 4),
                c.SetMemory(setptr_o + 20, c.Subtract, 2),
            ]
        )
    cs.EUDEndLoopN()
    f_setcurpl2cpcache()
    return textptr


def TextFX_Remove(tag):  # noqa: N802
    ut.ep_assert(tag is not None, "tag should not be None")
    _add_textfx_timer(tag)
    _, _, identifier = get_textfx_timer(tag)
    o0 = ut.b2i4(identifier[0:4])
    o1 = ut.b2i2(identifier[4:6])
    e0 = ut.b2i2(identifier[0:2]) * 0x10000
    e1 = ut.b2i4(identifier[2:6])
    return _remove_textfx(o0, o1, e0, e1)


_check_cp = c.Forward()
_is_below_start = c.Forward()
_cpbelowbuffer = c.EUDLightBool()


def _is_cp_less_than_start(actions):
    global _is_below_start
    if not _is_below_start.IsSet():
        c.PushTriggerScope()
        _is_below_start << c.RawTrigger(
            conditions=[_check_cp << c.Memory(0x6509B0, c.AtMost, 0)],
            actions=_cpbelowbuffer.Set(),
        )
        c.PopTriggerScope()
    _next = c.Forward()
    actions = ut.FlattenList(actions)
    c.RawTrigger(
        nextptr=_is_below_start,
        actions=[
            *actions,
            _cpbelowbuffer.Clear(),
            c.SetNextPtr(_is_below_start, _next),
        ],
    )
    _next << c.NextTrigger()


def _r2l(colors, colors_dict={}):
    try:
        _f = colors_dict[colors]
    except KeyError:

        @c.EUDFunc
        def _f():
            _jump, _isend, _end = (c.Forward() for _ in range(3))
            ret = c.EUDVariable()
            _is_cp_less_than_start([ret.SetNumber(1), c.SetNextPtr(_isend, _jump)])
            _isend << c.RawTrigger(
                conditions=_cpbelowbuffer.IsSet(),
                actions=[ret.SetNumber(0), c.SetNextPtr(_isend, _end)],
            )
            _jump << c.NextTrigger()
            for color in reversed(colors):
                _is_cp_less_than_start([])
                c.RawTrigger(
                    conditions=_cpbelowbuffer.IsCleared(),
                    actions=[
                        c.SetDeathsX(CurrentPlayer, c.SetTo, color, 0, 0xFF),
                        c.AddCurrentPlayer(-1),
                    ],
                )
            _end << c.NextTrigger()
            return ret

        colors_dict[colors] = _f
    return _f()


def _textfx_print(*args, identifier, encoding="UTF-8"):
    f_cpstr_print(identifier, EOS=False, encoding=encoding)
    global color_code
    color_code = b"\x02"
    color_v << 2

    args = ut.FlattenList(args)
    for arg in args:
        if isinstance(arg, str) and "\n" in arg:
            line = arg.split("\n")
            for s in line[:-1]:
                f_cpchar_print(s, EOS=False, encoding=encoding)
                f_cpstr_print(
                    identifier + b"\n" + identifier,
                    EOS=False,
                    encoding=encoding,
                )
            f_cpchar_print(line[-1], EOS=False, encoding=encoding)
        else:
            f_cpchar_print(arg, EOS=False, encoding=encoding)

    cs.DoActions(c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0))


def TextFX_FadeIn(  # noqa: N802
    *args, color=None, wait=1, reset=True, tag=None, encoding="UTF-8"
):
    """Print multiple string / number and apply color from Left To Right

    Keyword arguments:
    color -- tuple of color codes (default 0x03, 0x04, 0x05, 0x14)
    wait  -- time interval between effect (default 1)
    reset -- automatically reset when didn't run for a moment (default True)
    tag   -- internal tag and identifier (default: vargs)
    """
    from ..eudlib.utilf.gametick import f_getgametick

    if color is None:
        color = (0x03, 0x04, 0x05, 0x14)
    if tag is None:
        if len(args) == 1:
            tag = args[0]
        else:
            tag = args

    _add_textfx_timer(tag)
    timer, counter, identifier = get_textfx_timer(tag)

    start = f_getcurpl()
    c.VProc(
        start,
        [
            start.AddNumber(1),
            start.SetDest(ut.EPD(_check_cp) + 2),
        ],
    )
    _textfx_print(*args, identifier=identifier, encoding=encoding)
    f_setcurpl(start, actions=[start.AddNumber(2 - len(color))], set_modifier=False)

    if reset is True:
        check_gametick = c.Forward()
        if cs.EUDIf()([check_gametick << c.Memory(0x57F23C, c.AtLeast, 0)]):
            gametick = f_getgametick()
            c.VProc(
                gametick,
                [
                    timer.SetNumber(0),
                    gametick.AddNumber(1),
                    gametick.SetDest(ut.EPD(check_gametick) + 2),
                ],
            )
        cs.EUDEndIf()

    _is_finished, _draw_color, _end = (c.Forward() for _ in range(3))
    ret = c.EUDVariable()

    cs.DoActions(
        c.SetMemory(check_gametick + 8, c.Add, 1) if reset is True else [],
        c.SetNextPtr(_is_finished, _draw_color),
        c.AddCurrentPlayer(timer),
    )
    _is_finished << c.RawTrigger(
        conditions=[
            c.Deaths(CurrentPlayer, c.Exactly, 0, 0),
            timer.AtLeast(2 + len(color)),
        ],
        actions=[
            ret.SetNumber(0),
            counter.SetNumber(0),
            c.SetNextPtr(_is_finished, _end),
        ],
    )
    _draw_color << c.RawTrigger(
        actions=[
            ret.SetNumber(1),
            counter.AddNumber(1),
            c.AddCurrentPlayer(len(color) - 1),
        ]
    )
    _r2l(color)
    c.RawTrigger(
        conditions=counter.AtLeast(max(wait, 1)),
        actions=[counter.SetNumber(0), timer.AddNumber(1)],
    )
    _end << c.NextTrigger()
    return ret


def TextFX_FadeOut(  # noqa: N802
    *args, color=None, wait=1, reset=True, tag=None, encoding="UTF-8"
):
    """Print multiple string / number and apply color from Left To Right

    Keyword arguments:
    color -- tuple of color codes (default 0x03, 0x04, 0x05, 0x14)
    wait  -- time interval between effect (default 1)
    reset -- automatically reset when didn't run for a moment (default True)
    tag   -- internal tag and identifier (default: vargs)
    """
    from ..eudlib.utilf.gametick import f_getgametick

    if color is None:
        color = (0x03, 0x04, 0x05, 0x14)
    if tag is None:
        if len(args) == 1:
            tag = args[0]
        else:
            tag = args

    _add_textfx_timer(tag)
    timer, counter, identifier = get_textfx_timer(tag)

    start = f_getcurpl()
    c.VProc(
        start,
        [
            start.AddNumber(1),
            start.SetDest(ut.EPD(_check_cp) + 2),
        ],
    )
    _textfx_print(*args, identifier=identifier, encoding=encoding)

    if reset is True:
        check_gametick = c.Forward()
        if cs.EUDIf()([check_gametick << c.Memory(0x57F23C, c.AtLeast, 0)]):
            gametick = f_getgametick()
            c.VProc(
                gametick,
                [
                    timer.SetNumber(0),
                    gametick.AddNumber(1),
                    gametick.SetDest(ut.EPD(check_gametick) + 2),
                ],
            )
        cs.EUDEndIf()

    does_last_color_overwrite = color[-1] in {0, 5, 0x14}
    increment_and_jump, paint_last_color = c.Forward(), c.Forward()

    cs.DoActions(
        c.SetMemory(check_gametick + 8, c.Add, 1) if reset is True else [],
        c.AddCurrentPlayer((len(color) - 1) - timer),
        c.SetNextPtr(increment_and_jump, paint_last_color)
        if does_last_color_overwrite
        else [],
    )
    ret = _r2l(color)
    if does_last_color_overwrite:
        skip = c.Forward()
        increment_and_jump << c.RawTrigger(
            conditions=ret.Exactly(1),
            actions=[
                counter.AddNumber(1),
                c.SetNextPtr(increment_and_jump, skip),
            ],
        )
        paint_last_color << c.VProc(
            start,
            [
                start.AddNumber(1),
                start.SetDest(ut.EPD(0x6509B0)),
            ],
        )
        f_setcurpl2cpcache(
            [], c.SetDeathsX(CurrentPlayer, c.SetTo, color[-1], 0, 0xFF)
        )
        skip << c.NextTrigger()
    else:
        c.RawTrigger(conditions=ret.Exactly(1), actions=counter.AddNumber(1))
    c.RawTrigger(
        conditions=counter.AtLeast(max(wait, 1)),
        actions=[counter.SetNumber(0), timer.AddNumber(1)],
    )
    return ret
