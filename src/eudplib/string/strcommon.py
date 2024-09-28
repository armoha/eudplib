# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
import random

from typing_extensions import Self

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.mapdata.stringmap import ForceAddString
from ..memio.rwcommon import br1, bw1, cw

_strcommon = None


def temp_string_id():
    global _strcommon
    if _strcommon is None:
        _strcommon = ForceAddString("")
    return _strcommon


class ptr2s:  # noqa: N801
    def __init__(self, value):
        self._value = value


class epd2s:  # noqa: N801
    def __init__(self, value):
        self._value = value


class hptr:  # noqa: N801
    def __init__(self, value):
        self._value = value


dbstr_cont, cp_cont = c.Forward(), c.Forward()
count = c.EUDLightVariable(0)
key1 = random.randint(1, 0xFF)
key2 = random.randint(1, 0xFF)
key3 = random.randint(1, 0xFF)
key4 = random.randint(1, 0xFF)

c.PushTriggerScope()
init = [
    c.SetMemoryX(dbstr_cont + 380, c.Add, key1, 0xAA),
    c.SetMemoryX(dbstr_cont + 380, c.Add, key1, 0x55),
    c.SetMemoryX(dbstr_cont + 412, c.Add, key2, 0xAA),
    c.SetMemoryX(dbstr_cont + 412, c.Add, key2, 0x55),
]
dbstr_start = c.RawTrigger(actions=ut._rand_lst(init))
if cs.EUDWhileNot()(count >= 0x80000000):
    b = br1.readbyte()
    set_read = c.SetNextPtr(br1._read, 0)
    for i in ut._rand_lst(range(4)):
        c.RawTrigger(
            conditions=c.Memory(br1._read + 4, c.Exactly, br1._case[i]),
            actions=[
                c.SetMemory(set_read + 20, c.SetTo, br1._case[(i + 2) % 4]),
                [] if i <= 1 else c.SetMemory(br1._read + 348, c.Add, 1),
            ],
        )
    dbstr_cont << c.RawTrigger(
        actions=[
            count.AddNumber(0),
            b.AddNumberX(0, 0xAA),
            b.AddNumberX(0, 0x55),
            c.SetMemory(br1._read + 348, c.Add, -1),
            set_read,
        ]
    )
    bw1.writebyte(b)
cs.EUDEndWhile()
dbstr_end = c.RawTrigger(
    nextptr=0,
    actions=[
        count.SetNumber(0),
        c.SetMemory(dbstr_cont + 380, c.SetTo, 0),
        c.SetMemory(dbstr_cont + 412, c.SetTo, 0),
    ],
)

init = [
    c.SetMemoryX(cp_cont + 380, c.Add, key3, 0xAA),
    c.SetMemoryX(cp_cont + 380, c.Add, key3, 0x55),
    c.SetMemoryX(cp_cont + 412, c.Add, key4, 0xAA),
    c.SetMemoryX(cp_cont + 412, c.Add, key4, 0x55),
]
cp_start = c.RawTrigger(actions=ut._rand_lst(init))
if cs.EUDWhileNot()(count >= 0x80000000):
    b = br1.readbyte()
    set_read = c.SetNextPtr(br1._read, 0)
    for i in ut._rand_lst(range(4)):
        c.RawTrigger(
            conditions=c.Memory(br1._read + 4, c.Exactly, br1._case[i]),
            actions=[
                c.SetMemory(set_read + 20, c.SetTo, br1._case[(i + 2) % 4]),
                [] if i <= 1 else c.SetMemory(br1._read + 348, c.Add, 1),
            ],
        )
    cp_cont << c.RawTrigger(
        actions=[
            count.AddNumber(0),
            b.AddNumberX(0, 0xAA),
            b.AddNumberX(0, 0x55),
            c.SetMemory(br1._read + 348, c.Add, -1),
            set_read,
        ]
    )
    cw.writebyte(b)
cs.EUDEndWhile()
cw.flushdword()
cp_end = c.RawTrigger(
    nextptr=0,
    actions=[
        count.SetNumber(0),
        c.SetMemory(cp_cont + 380, c.SetTo, 0),
        c.SetMemory(cp_cont + 412, c.SetTo, 0),
    ],
)
c.PopTriggerScope()


class ObfuscatedBytes(c.EUDObject):
    __slots__ = ("_data", "_key")

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self) -> None:
        super().__init__()

        self._data = bytearray()
        self._key = random.randint(1, 255)

    def dbstr_print(self, b: bytes) -> None:
        ptr = self.find_or_add(b)
        nexttrg = c.Forward()
        randmax = 0xFFFFFFFF if len(b) == 1 else 0x80000000 // (len(b) - 1)
        add_count = random.randrange(0x80000000 // len(b) + 1, randmax)
        k1 = (self._key ^ key1) | (random.randint(0, 0xFFFFFF) << 8)
        k2 = (self._key ^ key2) | (random.randint(0, 0xFFFFFF) << 8)
        c.NonSeqCompute(
            [
                (ut.EPD(dbstr_cont) + 87, c.SetTo, add_count),
                (ut.EPD(dbstr_cont) + 95, c.SetTo, k1),
                (ut.EPD(dbstr_cont) + 103, c.SetTo, k2),
                *br1.seekepd(ut.EPD(ptr), subp=ptr % 4, operation=True),
                (ut.EPD(dbstr_end) + 1, c.SetTo, nexttrg),
            ]
        )
        c.SetNextTrigger(dbstr_start)
        nexttrg << c.NextTrigger()

    def cp_print(self, b: bytes) -> None:
        ptr = self.find_or_add(b)
        nexttrg = c.Forward()
        randmax = 0xFFFFFFFF if len(b) == 1 else 0x80000000 // (len(b) - 1)
        add_count = random.randrange(0x80000000 // len(b) + 1, randmax)
        k1 = (self._key ^ key3) | (random.randint(0, 0xFFFFFF) << 8)
        k2 = (self._key ^ key4) | (random.randint(0, 0xFFFFFF) << 8)
        c.NonSeqCompute(
            [
                (ut.EPD(cp_cont) + 87, c.SetTo, add_count),
                (ut.EPD(cp_cont) + 95, c.SetTo, k1),
                (ut.EPD(cp_cont) + 103, c.SetTo, k2),
                *br1.seekepd(ut.EPD(ptr), subp=ptr % 4, operation=True),
                (ut.EPD(cp_end) + 1, c.SetTo, nexttrg),
            ]
        )
        c.SetNextTrigger(cp_start)
        nexttrg << c.NextTrigger()

    def find(self, bb: bytes) -> int:
        ret = self._data.find(bb)
        if ret != -1:
            ret += len(bb) - 1
        return ret

    def find_or_add(self, b: bytes) -> c.ConstExpr:
        bb = bytes(x ^ self._key for x in b[::-1])
        find = self.find(bb)
        if find != -1:
            return self + find
        self._data.extend(bb)
        return self + len(self._data) - 1

    def DynamicConstructed(self) -> bool:  # noqa: N802
        return True

    def GetDataSize(self) -> int:  # noqa: N802
        return len(self._data)

    def WritePayload(self, pbuffer) -> None:  # noqa: N802
        pbuffer.WriteBytes(bytes(self._data))


_obfus = ObfuscatedBytes()
