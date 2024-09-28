# Copyright 2014-2019 by trgk, Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from ..memio.rwcommon import br1, bw1
from .dbstr import DBStringData
from .strcommon import _obfus, epd2s, hptr, ptr2s


def _add_str(dst, *, operations=[], _f=[]):
    try:
        start, end = _f[0], _f[1]
    except IndexError:
        c.PushTriggerScope()
        start = c.NextTrigger()
        jump, write, end = c.Forward(), c.Forward(), c.Forward()
        if cs.EUDInfLoop()():
            b = br1.readbyte()
            jump << c.RawTrigger(
                conditions=b.Exactly(0), actions=c.SetNextPtr(jump, end)
            )
            write << c.NextTrigger()
            bw1.writebyte(b)
            c.RawTrigger(actions=c.SetMemory(end + 380, c.Add, 1))
        cs.EUDEndInfLoop()

        end << c.RawTrigger(
            nextptr=0,
            actions=[
                c.SetMemoryEPD(0, c.Add, 0),
                c.SetMemory(end + 348, c.SetTo, 0),
                c.SetNextPtr(jump, write),
            ],
        )
        c.PopTriggerScope()

        _f.extend((start, end))

    if isinstance(dst, c.EUDVariable):
        dst = ut.EPD(dst.getValueAddr())
    nptr = c.Forward()
    _operations = [
        (ut.EPD(end) + 1, c.SetTo, nptr),
        (ut.EPD(end) + 86, c.SetTo, dst),
    ]
    if operations:
        _operations.extend(operations)
    c.NonSeqCompute(_operations)
    c.SetNextTrigger(start)
    nptr << c.NextTrigger()


@c.EUDFunc
def f_dbstr_addstr(dst, src):
    """Print string as string to dst. Same as strcpy except of return value.

    :param dst: Destination address (Not EPD player)
    :param src: Source address (Not EPD player)

    :returns: dst + strlen(src)
    """
    bw1.seekoffset(dst)
    br1.seekoffset(src)
    _add_str(dst)
    bw1.writebyte(0)

    return dst


@c.EUDFunc
def f_dbstr_addstr_epd(dst, epd):
    """Print string as string to dst. Same as strcpy except of return value.

    :param dst: Destination address (Not EPD player)
    :param epd: Source EPD player

    :returns: dst + strlen_epd(epd)
    """
    bw1.seekoffset(dst)
    br1.seekepd(epd)
    _add_str(dst)
    bw1.writebyte(0)

    return dst


def _add_dw(dst, number, *, operations=[], _f=[]):
    try:
        start, end, number_addr = _f[0], _f[1], _f[2]
    except IndexError:
        c.PushTriggerScope()
        start = c.NextTrigger()
        _number = c.EUDVariable()
        number_addr = ut.EPD(_number.getValueAddr())
        end = c.Forward()

        skipper = [c.Forward() for _ in range(9)]
        ch = [0] * 10

        # Get digits
        for i in range(10):
            _number, ch[i] = c.f_div(_number, 10)
            ch[i] += b"0"[0]
            if i != 9:
                cs.EUDJumpIf(_number == 0, skipper[i])

        # print digits
        for i in range(9, -1, -1):
            if i != 9:
                skipper[i] << c.NextTrigger()
            bw1.writebyte(ch[i])
            c.RawTrigger(actions=c.SetMemory(end + 348, c.Add, 1))

        end << c.RawTrigger(
            nextptr=0,
            actions=[
                c.SetMemoryEPD(0, c.Add, 0),
                c.SetMemory(end + 348, c.SetTo, 0),
            ],
        )
        c.PopTriggerScope()

        _f.extend((start, end, number_addr))

    if isinstance(dst, c.EUDVariable):
        dst = ut.EPD(dst.getValueAddr())
    nptr = c.Forward()
    _operations = [
        (ut.EPD(end) + 1, c.SetTo, nptr),
        (ut.EPD(end) + 86, c.SetTo, dst),
        (number_addr, c.SetTo, number),
    ]
    if operations:
        _operations.extend(operations)
    c.NonSeqCompute(_operations)
    c.SetNextTrigger(start)
    nptr << c.NextTrigger()


@c.EUDFunc
def f_dbstr_adddw(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)
    _add_dw(dst, number)
    bw1.writebyte(0)
    return dst


def _add_ptr(dst, number, *, operations=[], _f=[]):
    try:
        start, end, number_addr = _f[0], _f[1], _f[2]
    except IndexError:
        c.PushTriggerScope()
        start = c.NextTrigger()
        _number = c.EUDVariable()
        number_addr = ut.EPD(_number.getValueAddr())
        end = c.Forward()
        ch = [0] * 8

        # Get digits
        for i in range(8):
            _number, ch[i] = c.f_div(_number, 16)
        c.RawTrigger(actions=[c.AddNumber(b"0"[0]) for c in ch])

        # print digits
        for i in range(7, -1, -1):
            c.RawTrigger(
                conditions=ch[i].AtLeast(b"0"[0] + 10),
                actions=ch[i].AddNumber(b"A"[0] - b"0"[0] - 10),
            )
            bw1.writebyte(ch[i])

        end << c.RawTrigger(nextptr=0)
        c.PopTriggerScope()

        _f.extend((start, end, number_addr))

    nptr = c.Forward()
    _operations = [
        (dst, c.Add, 8),
        (ut.EPD(end) + 1, c.SetTo, nptr),
        (number_addr, c.SetTo, number),
    ]
    if operations:
        _operations.extend(operations)
    c.NonSeqCompute(_operations)
    c.SetNextTrigger(start)
    nptr << c.NextTrigger()


@c.EUDFunc
def f_dbstr_addptr(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)
    _add_ptr(dst, number)
    bw1.writebyte(0)
    return dst


def f_dbstr_print(dst, *args, EOS=True, encoding="UTF-8"):  # noqa: N803
    """Print multiple string / number to dst.

    :param dst: Destination address (Not EPD player)
    :param args: Things to print

    """
    ret = c.EUDVariable()
    ret << dst
    bw1.seekoffset(dst)
    static_len = 0

    for arg in ut.FlattenIter(args):
        try:
            arg = arg.fmt()
        except AttributeError:
            pass
        x = ut.unProxy(arg)
        if isinstance(x, str):
            x = x.encode(encoding)
        elif isinstance(x, int):
            # int and c.EUDVariable should act the same if possible.
            # EUDVariable has a value of 32bit unsigned integer.
            # So we adjust arg to be in the same range.
            x = str(x & 0xFFFFFFFF).encode(encoding)
        if isinstance(x, bytes):
            if x == b"":
                continue
            _obfus.dbstr_print(x)
            static_len += len(x)
        elif isinstance(x, c.Db | DBStringData):
            _add_str(ret, operations=br1.seekepd(ut.EPD(x), operation=True))
        elif isinstance(x, ptr2s):
            if c.IsEUDVariable(x._value):
                br1.seekoffset(x._value)
                _add_str(ret)
            else:
                _add_str(ret, operations=br1.seekoffset(x._value, operation=True))
        elif isinstance(x, epd2s):
            _add_str(ret, operations=br1.seekepd(x._value, operation=True))
        elif isinstance(x, hptr):
            _add_ptr(ret, x._value)
        elif isinstance(x, c.EUDVariable | c.ConstExpr):
            _add_dw(ret, x)
        else:
            e = _("Object with unknown parameter type {} given to {}")
            raise ut.EPError(e.format(arg, "f_dbstr_print"))

    if static_len:
        ret += static_len

    if EOS:
        bw1.writebyte(0)

    return ret
