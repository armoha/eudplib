# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
from typing import ClassVar

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...collections.eudarray import EUDArray
from ...maprw.injector.mainloop import (
    eud_onstart2,
    has_already_started,
)
from ...memio import (
    f_dwread_cp,
    f_epdread_epd,
    f_maskread_cp,
    f_repmovsd_epd,
    f_setcurpl2cpcache,
)
from ...scdata import CurrentPlayer, TrgUnit
from . import wiredata as wd

is64bit = c.EUDLightBool()
tranwire, grpwire, wirefram = c.EUDCreateVariables(3)
defaultwire = {}


def tranwire_default32():
    if "TranWire32" not in defaultwire:
        defaultwire["TranWire32"] = EUDArray(wd.TranWire32)
    return defaultwire["TranWire32"], wd.TranWire32


def grpwire_default32():
    if "GrpWire32" not in defaultwire:
        defaultwire["GrpWire32"] = EUDArray(wd.GrpWire32)
    return defaultwire["GrpWire32"], wd.GrpWire32


def wirefram_default32():
    if "Wirefram32" not in defaultwire:
        defaultwire["Wirefram32"] = EUDArray(wd.Wirefram32)
    return defaultwire["Wirefram32"], wd.Wirefram32


def tranwire_default64():
    if "TranWire64" not in defaultwire:
        defaultwire["TranWire64"] = EUDArray(wd.TranWire64)
    return defaultwire["TranWire64"], wd.TranWire64


def grpwire_default64():
    if "GrpWire64" not in defaultwire:
        defaultwire["GrpWire64"] = EUDArray(wd.GrpWire64)
    return defaultwire["GrpWire64"], wd.GrpWire64


def wirefram_default64():
    if "Wirefram64" not in defaultwire:
        defaultwire["Wirefram64"] = EUDArray(wd.Wirefram64)
    return defaultwire["Wirefram64"], wd.Wirefram64


class InitialWireframe:
    _collected: bool = False
    _tranwires: ClassVar[dict[int, int]] = {}
    _grpwires: ClassVar[dict[int, int]] = {}
    _wireframs: ClassVar[dict[int, int]] = {}

    @classmethod
    def _init(cls):
        global is64bit, tranwire, grpwire, wirefram
        f_epdread_epd(ut.EPD(0x68C1F4), ret=[tranwire])
        f_epdread_epd(ut.EPD(0x68C1FC), ret=[grpwire])
        f_epdread_epd(ut.EPD(0x68C204), ret=[wirefram])
        check_64bit = c.MemoryEPD(0, c.Exactly, 0)
        c.VProc(
            wirefram,
            [
                tranwire.AddNumber(1),
                grpwire.AddNumber(1),
                wirefram.AddNumber(1),
                c.SetMemory(check_64bit + 4, c.SetTo, 2),
                wirefram.QueueAddTo(ut.EPD(check_64bit) + 1),
            ],
        )
        if cs.EUDIf()(check_64bit):
            cs.DoActions(is64bit.Set())

            def create_init64(src, default, size):
                if src:
                    data = default[1]
                    init = [ut.i2b2(data[0])]
                    for n in range(size):
                        x = 2 * src[n] if n in src else 2 * n
                        if x == 2 * n:
                            init.append(bytes(8))
                        else:
                            init.append(ut.i2b2(data[x] >> 16))
                            init.append(ut.i2b4(data[x + 1]))
                            init.append(ut.i2b2(data[x + 2]))
                    init.append(ut.i2b2(data[-2] >> 16))
                    init.append(ut.i2b4(data[-1]))
                    init = c.Db(b"".join(init))
                    ut.ep_assert(
                        len(init.content) == (size + 1) * 8,
                        f"Size mismatch: {len(init.content)}",
                    )
                else:
                    init = default[0]
                return init if init._is_epd() else ut.EPD(init)

            tranwire_init = create_init64(cls._tranwires, tranwire_default64(), 106)
            grpwire_init = create_init64(cls._grpwires, grpwire_default64(), 131)
            wirefram_init = create_init64(cls._wireframs, wirefram_default64(), 228)

            f_repmovsd_epd(tranwire, tranwire_init, len(wd.TranWire64))
            f_repmovsd_epd(grpwire, grpwire_init, len(wd.GrpWire64))
            f_repmovsd_epd(wirefram, wirefram_init, len(wd.Wirefram64))
        if cs.EUDElse()():

            def init32(ptr, src, data):
                if not src:
                    return
                key_min = min(min(src.keys()), 5)  # Terran Siege Tank (Tank Mode)
                key_max = max(max(src.keys()), 87)  # Aldaris (Templar)

                def wf(n):
                    if n in src:
                        return 2 * src[n]
                    else:
                        return 2 * n

                init = [ut.i2b2(data[wf(key_min)])]
                for n in range(key_min, key_max + 1):
                    x = wf(n)
                    if x == 2 * n:
                        init.append(bytes(8))
                    else:
                        init.append(ut.i2b2(data[x] >> 16))
                        init.append(ut.i2b4(data[x + 1]))
                        init.append(ut.i2b2(data[x + 2]))
                init.append(ut.i2b2(data[x + 2] >> 16))
                init = c.Db(b"".join(init))
                ut.ep_assert(
                    len(init.content) == (key_max - key_min + 1) * 8 + 4,
                    f"Size mismatch: {len(init.content)}",
                )
                if key_min > 0:
                    ptr = ptr + 2 * key_min
                f_repmovsd_epd(ptr, ut.EPD(init), (key_max - key_min + 1) * 2 + 1)

            init32(tranwire, cls._tranwires, wd.TranWire32)
            init32(grpwire, cls._grpwires, wd.GrpWire32)
            init32(wirefram, cls._wireframs, wd.Wirefram32)
        cs.EUDEndIf()

    @classmethod
    def init(cls):
        ut.ep_assert(
            not has_already_started(),
            "Can't use EUDOnStart here. See https://cafe.naver.com/edac/69262",
        )
        if not cls._collected:
            cls._collected = True
            eud_onstart2(cls._init)

    @classmethod
    def _add(cls, unit, wireframe, length, wiredict):
        unit, wireframe = c.EncodeUnit(unit), c.EncodeUnit(wireframe)
        ut.ep_assert(
            isinstance(unit, int) and isinstance(wireframe, int),
            f"{unit} and {wireframe} should be valid unit",
        )
        if 0 <= unit < length and 0 <= wireframe < length:
            wiredict[unit] = wireframe
            cls.init()

    @classmethod
    def wireframes(cls, unit, wireframe):
        cls.tranwire(unit, wireframe)
        cls.grpwire(unit, wireframe)
        cls.wirefram(unit, wireframe)

    @classmethod
    def tranwire(cls, unit, wireframe):
        cls._add(unit, wireframe, 106, cls._tranwires)

    @classmethod
    def grpwire(cls, unit, wireframe):
        cls._add(unit, wireframe, 131, cls._grpwires)

    @classmethod
    def wirefram(cls, unit, wireframe):
        cls._add(unit, wireframe, 228, cls._wireframs)


def _set_wireframe(unit, wireframe, size, ptr, default32, default64):
    default32 = default32[0]
    default64 = default64[0]
    if not default32._is_epd():
        default32 = ut.EPD(default32)
    if not default64._is_epd():
        default64 = ut.EPD(default64)
    if cs.EUDIf()([unit <= size, wireframe <= size]):
        c.VProc(
            [unit, wireframe, ptr],
            [
                unit.QueueAddTo(unit),
                wireframe.QueueAddTo(wireframe),
                ptr.QueueAddTo(unit),
                c.SetMemory(0x6509B0, c.SetTo, default32),
            ],
        )
        c.RawTrigger(
            conditions=is64bit.IsSet(),
            actions=c.SetMemory(0x6509B0, c.SetTo, default64),
        )
        actions = [
            c.SetMemory(0x6509B0, c.SetTo, 0),
            c.SetDeathsX(CurrentPlayer, c.SetTo, 0, 0, 0xFFFF0000),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeathsX(CurrentPlayer, c.SetTo, 0, 0, 0xFFFF),
        ]
        c.VProc(
            [unit, wireframe],
            [
                unit.QueueAssignTo(ut.EPD(actions[0]) + 5),
                wireframe.SetDest(ut.EPD(0x6509B0)),
            ],
        )
        f_maskread_cp(0, 0xFFFF0000, ret=[ut.EPD(actions[1]) + 5])
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, 1))
        f_dwread_cp(0, ret=[ut.EPD(actions[3]) + 5])
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, 1))
        f_maskread_cp(0, 0xFFFF, ret=[ut.EPD(actions[5]) + 5])
        f_setcurpl2cpcache(actions=actions)
    cs.EUDEndIf()


@c.EUDTypedFunc([TrgUnit, TrgUnit])
def SetTranWire(unit, wireframe):  # noqa: N802
    InitialWireframe.init()
    _set_wireframe(
        unit, wireframe, 105, tranwire, tranwire_default32(), tranwire_default64()
    )


@c.EUDTypedFunc([TrgUnit, TrgUnit])
def SetGrpWire(unit, wireframe):  # noqa: N802
    InitialWireframe.init()
    _set_wireframe(
        unit, wireframe, 130, grpwire, grpwire_default32(), grpwire_default64()
    )


@c.EUDTypedFunc([TrgUnit, TrgUnit])
def SetWirefram(unit, wireframe):  # noqa: N802
    InitialWireframe.init()
    _set_wireframe(
        unit, wireframe, 227, wirefram, wirefram_default32(), wirefram_default64()
    )


@c.EUDTypedFunc([TrgUnit, TrgUnit])
def SetWireframes(unit, wireframe):  # noqa: N802
    InitialWireframe.init()
    SetTranWire(unit, wireframe)
    SetGrpWire(unit, wireframe)
    SetWirefram(unit, wireframe)


def Is64BitWireframe() -> c.Condition:  # noqa: N802
    """
    Check whether StarCraft is 32 bit or 64 bit, by inspecting wireframe.

    Local (desync) condition.
    Is64BitWireframe() loads custom wireframes,
    causing wireframe graphic glitches by StarCraft.
    """
    InitialWireframe.init()
    return is64bit.IsSet()
