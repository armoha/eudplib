#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut
from eudplib.core.allocator.payload import _RegisterAllocObjectsCallback
from eudplib.core.curpl import _curpl_checkcond, _curpl_var
from eudplib.core.mapdata.stringmap import get_string_section_name
from eudplib.localize import _

from ..memiof import f_dwread_epd, f_wread_epd

_STR_ADDRESS = 0x191943C8


@c.EUDTypedFunc([c.TrgString])
def _get_mapstring_addr(str_id):
    add_strptr, add_strepd = c.Forward(), c.Forward()
    if cs.EUDExecuteOnce()():
        strptr, strepd = _STR_ADDRESS, ut.EPD(_STR_ADDRESS)
        cs.DoActions(
            c.SetMemory(add_strptr + 20, c.SetTo, strptr),
            c.SetMemory(add_strepd + 20, c.SetTo, strepd),
        )
    cs.EUDEndExecuteOnce()
    str_chunk_name = get_string_section_name()
    if str_chunk_name == "STR":
        r, m = c.f_div(str_id, 2)
        c.RawTrigger(conditions=m.Exactly(1), actions=m.SetNumber(2))
        c.RawTrigger(actions=add_strepd << r.AddNumber(0))
        ret = f_wread_epd(r, m)
    elif str_chunk_name == "STRx":
        c.RawTrigger(actions=add_strepd << str_id.AddNumber(0))
        ret = f_dwread_epd(str_id)
    else:
        raise ut.EPError(_("Invalid string section name: {}").format(str_chunk_name))
    c.RawTrigger(actions=add_strptr << ret.AddNumber(0))
    c.EUDReturn(ret)


_const_strptr: dict[int, c.Forward] = {}


def _initialize_queries():
    from ...core.mapdata.stringmap import get_string_map

    strmap = get_string_map()
    strmap.finalize()
    non_existing_id = []
    for str_id, offset_query in _const_strptr.items():
        try:
            offset_query.Reset()
            offset_query << c.ConstExpr(
                None,
                _STR_ADDRESS + strmap._stroffset[strmap._dataindextb[str_id - 1]],
                0,
            )
        except IndexError:
            non_existing_id.append(str_id)

    if non_existing_id:
        raise ut.EPError(
            _("GetMapStringAddr(str_id) for non-existing string ID(s): {}").format(
                non_existing_id
            )
        )


_RegisterAllocObjectsCallback(_initialize_queries)


def GetMapStringAddr(str_id):  # noqa: N802
    global _const_strptr
    str_id = c.EncodeString(str_id)
    if isinstance(str_id, int):
        if str_id not in _const_strptr:
            _const_strptr[str_id] = c.Forward()
            _const_strptr[str_id] << 0
        return _const_strptr[str_id]
    return _get_mapstring_addr(str_id)


def _s2b(x):
    if isinstance(x, str):
        x = ut.u2utf8(x)
    if isinstance(x, bytes):
        x = x + b"\r" * (-(-len(x) // 4) * 4 - len(x))
    return x


def _addcpcache(p):
    p = c.EncodePlayer(p)
    return [
        _curpl_var.AddNumber(p),
        c.SetMemory(_curpl_checkcond + 8, c.Add, p),
    ]


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
            raise ut.EPError(
                _("Unexpected type for CPString: {}").format(type(content))
            )

        self.length = len(self.content) // 4
        self.trigger = list()
        self.valueAddr = [0 for _ in range(self.length)]
        actions = [
            [
                c.SetDeaths(
                    c.CurrentPlayer,
                    c.SetTo,
                    ut.b2i4(self.content[i : i + 4]),
                    i // 48,
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
                c.SetMemory(0x6509B0, c.Add, modlength) if modlength else [],
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

    def Display(self, action=[]):  # noqa: N802
        _next = c.Forward()
        c.RawTrigger(
            nextptr=self.trigger[0],
            actions=[action, c.SetNextPtr(self.trigger[-1], _next)],
        )
        _next << c.NextTrigger()

    def GetVTable(self):  # noqa: N802
        return self.trigger[0]
