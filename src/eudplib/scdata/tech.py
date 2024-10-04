# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar

from .. import core as c
from .. import memio
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.typehint import _Tech
from ..localize import _
from .offsetmap import (
    ByteMember,
    EPDOffsetMap,
    IconMember,
    RaceResearchMember,
    StatTextMember,
    WordMember,
)
from .player import TrgPlayer


class Tech(EPDOffsetMap, ConstType):
    __slots__ = ()
    mineralCost: ClassVar = WordMember("array", 0x656248)
    gasCost: ClassVar = WordMember("array", 0x6561F0)
    timeCost: ClassVar = WordMember("array", 0x6563D8)
    energyCost: ClassVar = WordMember("array", 0x656380)
    researchRequirementOffset: ClassVar = WordMember("array", 0x656198)
    techUseRequirementOffset: ClassVar = WordMember("array", 0x6562F8)
    icon: ClassVar = IconMember("array", 0x656430)
    label: ClassVar = StatTextMember("array", 0x6562A0)
    race: ClassVar = RaceResearchMember("array", 0x656488)
    researched: ClassVar = ByteMember("array", 0x656350)  # UNUSED?
    broodWarFlag: ClassVar = ByteMember("array", 0x6564B4)  # bool?

    @ut.classproperty
    def range(self):
        return (0, 43, 1)

    @classmethod
    def cast(cls, _from: _Tech):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval: _Tech) -> None:
        super().__init__(c.EncodeTech(initval))

    def _current_tech_epd_subp(self, player: TrgPlayer | int):
        r: c.EUDVariable
        sc_researched = 0x58CF44
        bw_researched = 0x58F140
        t = self._value
        if isinstance(player, TrgPlayer):
            p = player._value
        else:
            p = player
        if isinstance(p, int) or isinstance(player, int):
            ut.ep_assert(
                0 <= p <= 11,
                _("To get current tech, player must be in range from P1 to P12"),
            )
            if isinstance(t, c.EUDVariable):
                # (case 1) player is const, tech is var
                q, r, update = self._get_stride_cache(1)  # type: ignore[assignment]
                update_start, update_restore, update_end = update
                branch, sc_branch, bw_branch = (c.Forward() for _ in range(3))
                epd, subp = c.EUDCreateVariables(2)
                # Trigger 1: update tech cache and initialize epd, subp
                c.RawTrigger(
                    nextptr=update_start,
                    actions=[
                        c.SetNextPtr(update_start, update_restore),
                        c.SetMemory(update_start + 348, c.SetTo, q.GetVTable()),
                        c.SetNextPtr(update_end, q.GetVTable()),
                        c.SetNextPtr(q.GetVTable(), r.GetVTable()),
                        c.SetNextPtr(r.GetVTable(), branch),
                        q.QueueAssignTo(epd),
                        r.QueueAssignTo(subp),
                    ],
                )
                # Trigger 2: conditional branch for SC and BW tech
                branch << c.RawTrigger(
                    nextptr=sc_branch,
                    conditions=t.AtLeast(24),
                    actions=c.SetNextPtr(branch, bw_branch),
                )
                # (SC) Trigger 3: add to epd
                sc_branch << c.NextTrigger()
                epd += p * 24 // 4
                end = c.Forward()
                c.SetNextTrigger(end)
                # (BW) Trigger 3: add to epd
                bw_branch << c.NextTrigger()
                epd += p * 20 // 4 - (24 // 4)
                end << c.NextTrigger()
            # (case 2) player is const, tech is const
            elif t < 24:
                quotient, remainder = divmod(sc_researched + t + p * 24, 4)
                return quotient + ut.EPD(0), remainder
            else:
                quotient, remainder = divmod(bw_researched + t - 24 + p * 20, 4)
                return quotient + ut.EPD(0), remainder

        elif isinstance(t, c.EUDVariable):
            # (case 3) player is var, tech is var
            q_tech, r_tech, update_tech = self._get_stride_cache(1)
            if not isinstance(r_tech, c.EUDVariable):
                assert False
            t_update_start, t_update_restore, t_update_end = update_tech
            q24, r24, update_player = player._get_stride_cache(24)
            q20, r20, _update = player._get_stride_cache(20)
            p_update_start, p_update_restore, p_update_end = update_player

            # Trigger 1: update tech cache
            update_p, tech_branch = c.Forward(), c.Forward()
            c.RawTrigger(
                nextptr=t_update_start,
                actions=[
                    c.SetNextPtr(t_update_start, t_update_restore),
                    c.SetMemory(t_update_start + 348, c.SetTo, update_p),
                    c.SetNextPtr(t_update_end, update_p),
                ],
            )
            # Trigger 2: update player cache and initialize epd, subp
            # Can't update both tech and player at the same time
            # because t_update_end and p_update_end can be aliased.
            sc_branch, bw_branch = c.Forward(), c.Forward()
            epd, subp = c.EUDCreateVariables(2)
            update_p << c.VProc(
                [q_tech, r_tech],
                [
                    q_tech.QueueAssignTo(epd),
                    r_tech.QueueAssignTo(subp),
                    c.SetNextPtr(p_update_start, p_update_restore),
                    c.SetMemory(p_update_start + 348, c.SetTo, tech_branch),
                    c.SetNextPtr(p_update_end, tech_branch),
                    # prepare conditional branch
                    c.SetNextPtr(tech_branch, sc_branch),
                ],
            )
            c.SetNextTrigger(p_update_start)
            # Trigger 3: conditional branch for SC and BW tech
            tech_branch << c.RawTrigger(
                nextptr=sc_branch,
                conditions=t.AtLeast(24),
                actions=c.SetNextPtr(tech_branch, bw_branch),
            )
            # (SC) Trigger 4: add to epd, subp
            sc_branch << c.NextTrigger()
            c.SetVariables(
                [epd, epd],
                [ut.EPD(sc_researched), q24],
                [c.Add, c.Add],
            )
            end = c.Forward()
            c.SetNextTrigger(end)
            # (BW) Trigger 4: add to epd, subp (subp can be negative)
            bw_branch << c.NextTrigger()
            c.SetVariables(
                [epd, epd],
                [ut.EPD(bw_researched) - 24 // 4, q20],
                [c.Add, c.Add],
            )
            end << c.NextTrigger()
        else:
            # (case 4) player is var, tech is const
            if t < 24:
                q, r, update = player._get_stride_cache(24)  # type: ignore[assignment]
                quotient, remainder = divmod(t, 4)
            else:
                q, r, update = player._get_stride_cache(20)  # type: ignore[assignment]
                quotient, remainder = divmod(t - 24, 4)
            update_start, update_restore, update_end = update
            nexttrg = c.Forward()
            c.RawTrigger(
                nextptr=update_start,
                actions=[
                    c.SetNextPtr(update_start, update_restore),
                    c.SetMemory(update_start + 348, c.SetTo, nexttrg),
                    c.SetNextPtr(update_end, nexttrg),
                ],
            )
            nexttrg << c.NextTrigger()
            if t < 24:
                epd = ut.EPD(sc_researched) + quotient + q
            else:
                epd = ut.EPD(bw_researched) + quotient + q
            subp = remainder

        return epd, subp

    def __getitem__(self, player: TrgPlayer | int) -> c.EUDVariable:
        from ..memio.bwepdio import _boolread_epd

        epd, subp = self._current_tech_epd_subp(player)
        return _boolread_epd(epd, subp)

    def __setitem__(self, player: TrgPlayer | int, level) -> None:
        epd, subp = self._current_tech_epd_subp(player)
        memio.f_bwrite_epd(epd, subp, level)
