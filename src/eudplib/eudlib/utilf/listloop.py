# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterator
from typing import ClassVar, Self

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...localize import _
from ...maprw.injector.mainloop import _on_game_loop_start
from ...memio import (
    f_bread_cp,
    f_cunitepdread_epd,
    f_dwepdread_epd,
    f_epdcunitread_epd,
    f_setcurpl2cpcache,
)
from ...memio import modcurpl as cp
from ...scdata import CUnit
from ...utils import EPD
from .unlimiterflag import IsUnlimiterOn


def EUDLoopList(  # noqa: N802
    header_offset, break_offset=None
) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    blockname = "listloop"
    ut.EUDCreateBlock(blockname, header_offset)

    ptr, epd = f_dwepdread_epd(ut.EPD(header_offset))

    if break_offset is not None:
        cs.EUDWhileNot()(ptr == break_offset)
    else:
        cs.EUDWhile()([ptr > 0, ptr <= 0x7FFFFFFF])

    yield ptr, epd
    cs.EUDSetContinuePoint()
    epd += 1
    f_dwepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.ep_assert(
        ut.EUDPopBlock(blockname)[1] is header_offset, _("listloop mismatch")
    )


def EUDLoopUnit() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:  # noqa: N802
    ut.EUDCreateBlock("unitloop", 0x628430)

    ptr, epd = f_cunitepdread_epd(EPD(0x628430))

    if cs.EUDWhile()(ptr >= 1):
        yield ptr, epd
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.EUDPopBlock("unitloop")


class _UniqueIdentifier(c.EUDObject):
    _instances: ClassVar[list[Self]] = []

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self) -> None:
        super().__init__()
        if not _UniqueIdentifier._instances:
            _on_game_loop_start(lambda: _UniqueIdentifier._init())
        _UniqueIdentifier._instances.append(self)

    def GetDataSize(self) -> int:  # noqa: N802
        return 4 + 336 * 1699

    def WritePayload(self, emitbuffer) -> None:  # noqa: N802
        emitbuffer.WriteDword(0)
        for _unit_data in range(1699):
            emitbuffer.WriteSpace(332)
            emitbuffer.WriteDword(0)

    @classmethod
    def _init(cls):
        first_empty_unir_ptr = EPD(0x628438)
        epd = f_epdcunitread_epd(first_empty_unir_ptr)
        quot, rem = divmod(len(_UniqueIdentifier._instances), 32)
        endflags = c.Db((len(_UniqueIdentifier._instances) + 7) // 8)
        cs.DoActions(
            *[c.SetMemory(endflags + 4 * i, c.SetTo, 0) for i in range(quot)],
            c.SetMemoryX(endflags + 4 * quot, c.SetTo, 0, (1 << rem) - 1)
            if rem > 0
            else [],
        )
        if cs.EUDWhileNot()(epd == 0):
            c.VProc(
                epd,
                [
                    c.SetMemory(0x6509B0, c.SetTo, 0xA5 // 4),
                    epd.QueueAddTo(EPD(0x6509B0)),
                ],
            )
            uniq = f_bread_cp(0, 1)
            for i, unique_identifier in enumerate(_UniqueIdentifier._instances):
                q, r = divmod(i, 32)
                check_unique = c.DeathsX(cp.CP, c.Exactly, 0, 0, 0xFF)
                if cs.EUDIfNot()(c.MemoryX(endflags + 4 * q, c.AtLeast, 1, 1 << r)):
                    prev = (
                        EPD(0x59CCA8) + 0xA5 // 4
                        if i == 0
                        else EPD(_UniqueIdentifier._instances[i - 1])
                    )
                    c.VProc(
                        uniq,
                        [
                            c.SetMemory(0x6509B0, c.Add, -prev),
                            c.SetMemory(0x6509B0, c.Add, EPD(unique_identifier)),
                            uniq.SetDest(EPD(check_unique + 8)),
                        ],
                    )
                    if cs.EUDIf()(check_unique):
                        cs.DoActions(
                            c.SetMemoryX(endflags + 4 * q, c.SetTo, 1 << r, 1 << r)
                        )
                    if cs.EUDElse()():
                        c.VProc(uniq, uniq.SetDest(cp.CP))
                    cs.EUDEndIf()
                cs.EUDEndIf()
            cs.EUDBreakIf(
                [
                    *[
                        c.Memory(endflags + 4 * i, c.Exactly, 0xFFFFFFFF)
                        for i in range(quot)
                    ],
                    c.MemoryX(
                        endflags + 4 * quot,
                        c.Exactly,
                        (1 << rem) - 1,
                        (1 << rem) - 1,
                    )
                    if rem > 0
                    else [],
                ]
            )
            cs.EUDSetContinuePoint()
            epd += 1
            f_epdcunitread_epd(epd, ret=[epd])
        cs.EUDEndWhile()
        f_setcurpl2cpcache()


def EUDLoopNewUnit(  # noqa: N802
    allowance: int = 2,
) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    unique_identifier = _UniqueIdentifier()
    ut.ep_assert(isinstance(allowance, int))
    first_unit_ptr = EPD(0x628430)
    ut.EUDCreateBlock("newunitloop", "newlo")
    tos0 = c.EUDLightVariable(0)
    # tos0 << 0

    ptr, epd = f_cunitepdread_epd(first_unit_ptr)
    if cs.EUDWhileNot()(ptr == 0):
        c.VProc(
            epd,
            [
                c.SetMemory(0x6509B0, c.SetTo, 0xA5 // 4),
                epd.QueueAddTo(EPD(0x6509B0)),
            ],
        )
        uniq = f_bread_cp(0, 1)
        check_unique = c.DeathsX(cp.CP, c.Exactly, 0, 0, 0xFF)
        c.VProc(
            uniq,
            [
                c.SetMemory(
                    0x6509B0,
                    c.Add,
                    EPD(unique_identifier) - EPD(0x59CCA8) - 0xA5 // 4,
                ),
                uniq.SetDest(EPD(check_unique + 8)),
            ],
        )
        if cs.EUDIfNot()(check_unique):
            f_setcurpl2cpcache(uniq, uniq.SetDest(cp.CP))
            yield ptr, epd
        if cs.EUDElse()():
            tos0 += 1
            cs.EUDBreakIf(tos0.AtLeast(allowance))
        cs.EUDEndIf()
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    f_setcurpl2cpcache([], tos0.SetNumber(0))
    ut.EUDPopBlock("newunitloop")


def EUDLoopUnit2() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:  # noqa: N802
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    if IsUnlimiterOn():
        offset, is_dead = 0x4C // 4, c.MemoryXEPD(0, c.Exactly, 0, 0xFF00)
    else:
        offset, is_dead = 0x0C // 4, c.MemoryEPD(0, c.Exactly, 0)
    ptr = c.EUDVariable()
    epd = c.EUDVariable()
    continue_if = c.Forward()
    set_ptr, set_epd = ptr.SetNumber(0), epd.SetNumber(0)

    cs.DoActions(
        ptr.SetNumber(0x59CCA8),
        c.SetMemory(set_ptr + 20, c.SetTo, 0x59CCA8),
        epd.SetNumber(EPD(0x59CCA8)),
        c.SetMemory(is_dead + 4, c.SetTo, EPD(0x59CCA8) + offset),
        c.SetMemory(set_epd + 20, c.SetTo, EPD(0x59CCA8)),
    )
    if cs.EUDWhileNot()(ptr >= 0x59CCA8 + 336 * 1699 + 1):
        whileblock = ut.EUDPeekBlock("whileblock")[1]
        c.PushTriggerScope()
        continue_okay = c.Forward()
        continue_jump = c.RawTrigger(
            nextptr=whileblock["contpoint"],
            actions=c.SetNextPtr(continue_if, continue_okay),
        )
        c.PopTriggerScope()
        continue_if << c.RawTrigger(
            conditions=is_dead, actions=c.SetNextPtr(continue_if, continue_jump)
        )
        continue_okay << c.NextTrigger()
        yield ptr, epd

        cs.EUDSetContinuePoint()
        c.RawTrigger(
            nextptr=whileblock["loopstart"],
            actions=[
                c.SetMemory(is_dead + 4, c.Add, 84),
                c.SetMemory(set_ptr + 20, c.Add, 336),
                set_ptr,
                c.SetMemory(set_epd + 20, c.Add, 84),
                set_epd,
            ],
        )
    cs.EUDEndWhile()


def EUDLoopPlayerUnit(player) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:  # noqa: N802
    player = c.EncodePlayer(player)
    first_player_unit = 0x6283F8
    ut.EUDCreateBlock("playerunitloop", first_player_unit)
    ptr, epd = f_cunitepdread_epd(ut.EPD(first_player_unit) + player)

    if cs.EUDWhile()(ptr >= 1):
        next_unit, nextptr = c.Forward(), c.Forward()
        # /*0x06C*/ BW::CUnit*  nextPlayerUnit;
        # f_cunitepdread_epd(
        #     epd + 0x6C // 4,
        #     ret=[EPD(next_unit) + 5, EPD(next_unit) + 13]
        # )
        c.VProc(
            epd,
            [
                c.SetMemory(0x6509B0, c.SetTo, 0x6C // 4),
                epd.QueueAddTo(EPD(0x6509B0)),
                f_cunitepdread_epd._frets[0].SetDest(EPD(next_unit) + 5),
                f_cunitepdread_epd._frets[1].SetDest(EPD(next_unit) + 13),
                c.SetMemory(f_cunitepdread_epd._nptr, c.SetTo, nextptr),
            ],
        )
        c.SetNextTrigger(f_cunitepdread_epd._fstart)
        nextptr << c.NextTrigger()
        yield ptr, epd
        cs.EUDSetContinuePoint()
        cs.DoActions(next_unit << ptr.SetNumber(0), epd.SetNumber(0))
    cs.EUDEndWhile()

    ut.EUDPopBlock("playerunitloop")


def EUDLoopBullet() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:  # noqa: N802
    yield from EUDLoopList(0x64DEC4)


def EUDLoopSprite() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:  # noqa: N802
    y_epd = c.EUDVariable()
    y_epd << ut.EPD(0x629688)

    ut.EUDCreateBlock("spriteloop", "sprlo")

    if cs.EUDWhile()(y_epd < ut.EPD(0x629688) + 256):
        ptr, epd = f_dwepdread_epd(y_epd)
        if cs.EUDWhile()(ptr >= 1):
            yield ptr, epd
            cs.EUDSetContinuePoint()
            epd += 1
            f_dwepdread_epd(epd, ret=[ptr, epd])
        cs.EUDEndWhile()
        y_epd += 1
    cs.EUDEndWhile()

    ut.EUDPopBlock("spriteloop")


def EUDLoopNewCUnit(allowance: int = 2) -> Iterator[CUnit]:  # noqa: N802
    for ptr, epd in EUDLoopNewUnit(allowance):
        yield CUnit.cast(epd, ptr=ptr)


def EUDLoopCUnit() -> Iterator[CUnit]:  # noqa: N802
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    for ptr, epd in EUDLoopUnit2():
        yield CUnit.cast(epd, ptr=ptr)


def EUDLoopPlayerCUnit(player) -> Iterator[CUnit]:  # noqa: N802
    for ptr, epd in EUDLoopPlayerUnit(player):
        yield CUnit.cast(epd, ptr=ptr)
