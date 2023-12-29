#!/usr/bin/python
# Copyright 2014-2019 by trgk, Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..stringf.rwcommon import br1, bw1
from .dbstr import DBString

_conststr_dict = dict()
_str_jump, _str_eos, _str_dst = c.Forward(), c.Forward(), c.Forward()
_dw_jump, _dw_eos, _dw_dst = c.Forward(), c.Forward(), c.Forward()
_ptr_jump, _ptr_eos, _ptr_dst = c.Forward(), c.Forward(), c.Forward()


def _addstr_core(_f=[]):
    if not _str_jump.IsSet():

        def f():
            global _str_jump, _str_eos, _str_dst
            c.PushTriggerScope()
            strlen = c.EUDVariable()
            init = c.RawTrigger(actions=strlen.SetNumber(0))
            write = c.Forward()

            if cs.EUDInfLoop()():
                b = br1.readbyte()
                _str_jump << c.RawTrigger(
                    conditions=b.Exactly(0),
                    actions=c.SetNextPtr(_str_jump, _str_eos),
                )
                write << c.NextTrigger()
                bw1.writebyte(b)
                strlen += 1
            cs.EUDEndInfLoop()

            _str_eos << c.NextTrigger()
            bw1.writebyte(0)  # EOS
            _str_dst << c.RawTrigger(actions=c.SetNextPtr(_str_jump, write))
            c.PopTriggerScope()

            return init, _str_dst, strlen

        _f.extend(f())

    init, end, strlen = _f
    nptr = c.Forward()
    c.RawTrigger(nextptr=init, actions=c.SetNextPtr(end, nptr))
    nptr << c.NextTrigger()

    return strlen


@c.EUDFunc
def f_dbstr_addstr(dst, src):
    """Print string as string to dst. Same as strcpy except of return value.

    :param dst: Destination address (Not EPD player)
    :param src: Source address (Not EPD player)

    :returns: dst + strlen(src)
    """
    bw1.seekoffset(dst)
    br1.seekoffset(src)
    strlen = _addstr_core()
    dst += strlen

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
    strlen = _addstr_core()
    dst += strlen

    return dst


@c.EUDFunc
def _addstr(src):
    br1.seekoffset(src)
    return _addstr_core()


@c.EUDFunc
def _addstr_epd(epd):
    br1.seekepd(epd)
    return _addstr_core()


@c.EUDFunc
def _adddw(number):
    global _dw_jump, _dw_eos, _dw_dst
    strlen = c.EUDVariable()
    strlen << 0

    skipper = [c.Forward() for _ in range(9)]
    ch = [0] * 10

    # Get digits
    for i in range(10):
        number, ch[i] = c.f_div(number, 10)
        ch[i] += b"0"[0]
        if i != 9:
            cs.EUDJumpIf(number == 0, skipper[i])

    # print digits
    for i in range(9, -1, -1):
        if i != 9:
            skipper[i] << c.NextTrigger()
        bw1.writebyte(ch[i])
        if i == 0:
            _dw_jump << c.NextTrigger()
        strlen += 1

    _dw_eos << c.NextTrigger()
    bw1.writebyte(0)  # EOS
    _dw_dst << c.NextTrigger()

    return strlen


@c.EUDFunc
def f_dbstr_adddw(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)
    dst += _adddw(number)

    return dst


@c.EUDFunc
def _addptr(number):
    global _ptr_jump, _ptr_eos, _ptr_dst
    strlen = c.EUDVariable()
    strlen << 0
    ch = [0] * 8

    # Get digits
    for i in range(8):
        number, ch[i] = c.f_div(number, 16)

    # print digits
    for i in range(7, -1, -1):
        if cs.EUDIf()(ch[i] <= 9):
            bw1.writebyte(ch[i] + b"0"[0])
        if cs.EUDElse()():
            bw1.writebyte(ch[i] + (b"A"[0] - 10))
        cs.EUDEndIf()
        if i == 0:
            _ptr_jump << c.NextTrigger()
        strlen += 1

    _ptr_eos << c.NextTrigger()
    bw1.writebyte(0)  # EOS
    _ptr_dst << c.NextTrigger()

    return strlen


@c.EUDFunc
def f_dbstr_addptr(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)
    dst += _addptr(number)

    return dst


def _omit_eos(*args):
    dw = any(
        (
            c.IsConstExpr(x)
            and not isinstance(x, (int, str, bytes))
            and not ut.isUnproxyInstance(x, c.Db)
        )
        or c.IsEUDVariable(x)
        for x in args
    )
    ptr = any(ut.isUnproxyInstance(x, hptr) for x in args)
    cs.DoActions(
        c.SetMemory(_str_jump + 348, c.SetTo, _str_dst),
        c.SetNextPtr(_dw_jump, _dw_dst) if dw else [],
        c.SetNextPtr(_ptr_jump, _ptr_dst) if ptr else [],
    )
    yield (dw, ptr)
    cs.DoActions(
        c.SetMemory(_str_jump + 348, c.SetTo, _str_eos),
        c.SetNextPtr(_dw_jump, _dw_eos) if dw else [],
        c.SetNextPtr(_ptr_jump, _ptr_eos) if ptr else [],
    )


class ptr2s:  # noqa: N801
    def __init__(self, value):
        self._value = value


class epd2s:  # noqa: N801
    def __init__(self, value):
        self._value = value


class hptr:  # noqa: N801
    def __init__(self, value):
        self._value = value


def f_dbstr_print(dst, *args, EOS=True, encoding="UTF-8"):  # noqa: N803
    """Print multiple string / number to dst.

    :param dst: Destination address (Not EPD player)
    :param args: Things to print

    """
    if ut.isUnproxyInstance(dst, DBString):
        dst = dst.GetStringMemoryAddr()

    args = ut.FlattenList(args)

    arg0f = {
        "str": f_dbstr_addstr,
        "epd": f_dbstr_addstr_epd,
        "dw": f_dbstr_adddw,
        "ptr": f_dbstr_addptr,
    }
    argnf = {"str": _addstr, "epd": _addstr_epd, "dw": _adddw, "ptr": _addptr}

    strlens = list()

    def proc_arg(index, arg):
        addf = argnf
        if index == 0:
            addf = arg0f

        def dstmsg(argument):
            if index == 0:
                nonlocal dst
                return (dst, argument)
            else:
                return (argument,)

        try:
            arg = arg.fmt()
        except AttributeError:
            pass
        if ut.isUnproxyInstance(arg, str):
            arg = arg.encode(encoding)
        elif ut.isUnproxyInstance(arg, int):
            # int and c.EUDVariable should act the same if possible.
            # EUDVariable has a value of 32bit unsigned integer.
            # So we adjust arg to be in the same range.
            arg = ut.u2b(str(arg & 0xFFFFFFFF))
        if ut.isUnproxyInstance(arg, bytes):
            if arg not in _conststr_dict:
                _conststr_dict[arg] = c.Db(arg + b"\0")
            arg = _conststr_dict[arg]
        if ut.isUnproxyInstance(arg, c.Db):
            strlen = addf["epd"](*dstmsg(ut.EPD(arg)))
        elif ut.isUnproxyInstance(arg, DBString):
            strlen = addf["epd"](*dstmsg(ut.EPD(arg.GetStringMemoryAddr())))
        elif ut.isUnproxyInstance(arg, epd2s):
            strlen = addf["epd"](*dstmsg(arg._value))
        elif ut.isUnproxyInstance(arg, ptr2s):
            strlen = addf["str"](*dstmsg(arg._value))
        elif c.IsEUDVariable(arg):
            strlen = addf["dw"](*dstmsg(arg))
        elif c.IsConstExpr(arg):
            strlen = addf["dw"](*dstmsg(arg))
        elif ut.isUnproxyInstance(arg, hptr):
            strlen = addf["ptr"](*dstmsg(arg._value))
        else:
            e = _("Object with unknown parameter type {} given to f_eudprint.")
            raise ut.EPError(e.format(type(arg)))
        strlens.append(strlen)

    if EOS:
        if len(args) >= 2:
            for _ in _omit_eos(*args):
                for i, arg in enumerate(args[:-1]):
                    proc_arg(i, arg)
            proc_arg(-1, args[-1])

            c.SeqCompute([(strlens[0], c.Add, strlen) for strlen in strlens[1:]])
        else:
            proc_arg(0, args[0])
    else:
        for _ in _omit_eos(*args):
            for i, arg in enumerate(args):
                proc_arg(i, arg)
        if len(args) >= 2:
            c.SeqCompute([(strlens[0], c.Add, strlen) for strlen in strlens[1:]])

    return strlens[0]
