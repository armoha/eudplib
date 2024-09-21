# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import core as c
from .. import memio
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk
from .player import TrgPlayer


class Upgrade(EPDOffsetMap, ConstType):
    __slots__ = ()
    mineralCostBase = ArrayMember(0x655740, Mk.WORD)
    mineralCostFactor = ArrayMember(0x6559C0, Mk.WORD)
    gasCostBase = ArrayMember(0x655840, Mk.WORD)
    gasCostFactor = ArrayMember(0x6557C0, Mk.WORD)
    timeCostBase = ArrayMember(0x655B80, Mk.WORD)
    timeCostFactor = ArrayMember(0x655940, Mk.WORD)
    requirementOffset = ArrayMember(0x6558C0, Mk.WORD)
    icon = ArrayMember(0x655AC0, Mk.ICON)
    label = ArrayMember(0x655A40, Mk.STATTEXT)
    race = ArrayMember(0x655BFC, Mk.RACE_RESEARCH)
    maxLevel = ArrayMember(0x655700, Mk.BYTE)
    broodWarFlag = ArrayMember(0x655B3C, Mk.BYTE)  # bool?

    @ut.classproperty
    def range(self):
        return (0, 60, 1)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(c.EncodeUpgrade(initval))

    def __getitem__(self, player: TrgPlayer | int) -> c.EUDVariable:
        r: c.EUDVariable
        sc_researched = 0x58D2B0
        bw_researched = 0x58F32C
        u = self._value
        if isinstance(player, TrgPlayer):
            p = player._value
        else:
            p = player
        if isinstance(p, int) or isinstance(player, int):
            ut.ep_assert(
                0 <= p <= 11,
                _("To get current upgrade, player must be in range from P1 to P12"),
            )
            if isinstance(u, c.EUDVariable):
                # (case 1) player is const, upgrade is var
                q, r, update = self._get_stride_cache(1)  # type: ignore[assignment]
                update_start, update_restore, update_end = update
                branch, sc_branch, bw_branch = (c.Forward() for _ in range(3))
                epd, subp = c.EUDCreateVariables(2)
                # Trigger 1: update upgrade cache and initialize epd, subp
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
                # Trigger 2: conditional branch for SC and BW upgrades
                branch << c.RawTrigger(
                    nextptr=sc_branch,
                    conditions=u.AtLeast(46),
                    actions=c.SetNextPtr(branch, bw_branch),
                )
                # (SC) Trigger 3: add to epd, subp
                sc_branch << c.NextTrigger()
                quotient, remainder = divmod(p * 46, 4)
                c.SetVariables(
                    [epd, subp],
                    [ut.EPD(sc_researched) + quotient, remainder],
                    [c.Add, c.Add],
                )
                # (SC) Trigger 4: carry 4 subp to 1 epd
                # max(r) = 3, max(remainder) = 2, max(subp) = 5
                end = c.Forward()
                c.RawTrigger(
                    conditions=subp.AtLeast(4),
                    actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
                )
                c.SetNextTrigger(end)
                # (BW) Trigger 3: add to epd, subp (subp can be negative)
                bw_branch << c.NextTrigger()
                quotient, remainder = divmod(p * 15, 4)
                q_off, r_off = divmod(46, 4)
                c.SetVariables(
                    [epd, subp],
                    [
                        ut.EPD(bw_researched) + quotient - q_off,
                        remainder - r_off,
                    ],
                    [c.Add, c.Add],
                )
                # (BW) Trigger 4: nagative subp borrow from epd
                c.RawTrigger(
                    conditions=subp.AtLeast(0x80000000),
                    actions=[subp.AddNumber(4), epd.AddNumber(-1)],
                )
                # (BW) Trigger 5: carry 4 subp to 1 epd
                # max(r) = 3, max(remainder) = 3, subp -= 2, max(subp) = 4
                c.RawTrigger(
                    conditions=subp.AtLeast(4),
                    actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
                )
                end << c.NextTrigger()
            # (case 2) player is const, upgrade is const
            elif u < 46:
                return memio.f_bread(sc_researched + u + p * 46)
            else:
                return memio.f_bread(bw_researched + u - 46 + p * 15)

        elif isinstance(u, c.EUDVariable):
            # (case 3) player is var, upgrade is var
            q_upgrade, r_upgrade, update_upgrade = self._get_stride_cache(1)
            if not isinstance(r_upgrade, c.EUDVariable):
                assert False
            u_update_start, u_update_restore, u_update_end = update_upgrade
            q46, r46, update_player = player._get_stride_cache(46)
            q15, r15, _update = player._get_stride_cache(15)
            p_update_start, p_update_restore, p_update_end = update_player

            # Trigger 1: update upgrade cache
            update_p, upgrade_branch = c.Forward(), c.Forward()
            c.RawTrigger(
                nextptr=u_update_start,
                actions=[
                    c.SetNextPtr(u_update_start, u_update_restore),
                    c.SetMemory(u_update_start + 348, c.SetTo, update_p),
                    c.SetNextPtr(u_update_end, update_p),
                ],
            )
            # Trigger 2: update player cache and initialize epd, subp
            # Can't update both upgrade and player at the same time
            # because u_update_end and p_update_end can be aliased.
            sc_branch, bw_branch = c.Forward(), c.Forward()
            epd, subp = c.EUDCreateVariables(2)
            update_p << c.VProc(
                [q_upgrade, r_upgrade],
                [
                    q_upgrade.QueueAssignTo(epd),
                    r_upgrade.QueueAssignTo(subp),
                    c.SetNextPtr(p_update_start, p_update_restore),
                    c.SetMemory(p_update_start + 348, c.SetTo, upgrade_branch),
                    c.SetNextPtr(p_update_end, upgrade_branch),
                    # prepare conditional branch
                    c.SetNextPtr(upgrade_branch, sc_branch),
                ],
            )
            c.SetNextTrigger(p_update_start)
            # Trigger 3: conditional branch for SC and BW upgrades
            upgrade_branch << c.RawTrigger(
                nextptr=sc_branch,
                conditions=u.AtLeast(46),
                actions=c.SetNextPtr(upgrade_branch, bw_branch),
            )
            # (SC) Trigger 4: add to epd, subp
            sc_branch << c.NextTrigger()
            c.SetVariables(
                [epd, epd, subp],
                [ut.EPD(sc_researched), q46, r46],
                [c.Add, c.Add, c.Add],
            )
            # (SC) Trigger 5: carry 4 subp to 1 epd
            # max(r_upgrade) = 3, max(r46) = 2, max(subp) = 5
            end = c.Forward()
            c.RawTrigger(
                conditions=subp.AtLeast(4),
                actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
            )
            c.SetNextTrigger(end)
            # (BW) Trigger 4: add to epd, subp (subp can be negative)
            bw_branch << c.NextTrigger()
            q_off, r_off = divmod(46, 4)
            c.SetVariables(
                [epd, subp, epd, subp],
                [ut.EPD(bw_researched) - q_off, -r_off, q15, r15],
                [c.Add, c.Add, c.Add, c.Add],
            )
            # (BW) Trigger 5: nagative subp borrow from epd
            c.RawTrigger(
                conditions=subp.AtLeast(0x80000000),
                actions=[subp.AddNumber(4), epd.AddNumber(-1)],
            )
            # (BW) Trigger 6: carry 4 subp to 1 epd
            # max(r_upgrade) = 3, max(r15) = 3, subp -= 2, max(subp) = 4
            c.RawTrigger(
                conditions=subp.AtLeast(4),
                actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
            )
            end << c.NextTrigger()
        else:
            # (case 4) player is var, upgrade is const
            if u < 46:
                q, r, update = player._get_stride_cache(46)  # type: ignore[assignment]
                quotient, remainder = divmod(u, 4)
            else:
                q, r, update = player._get_stride_cache(15)  # type: ignore[assignment]
                quotient, remainder = divmod(u - 46, 4)
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
            if u < 46:
                epd = ut.EPD(sc_researched) + quotient + q
            else:
                epd = ut.EPD(bw_researched) + quotient + q
            subp = remainder + r if remainder else r
            # carry 4 subp -> 1 epd
            if u < 46 and remainder >= 2:
                c.RawTrigger(
                    conditions=subp.AtLeast(4),
                    actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
                )
            elif u >= 46 and remainder >= 1:
                c.RawTrigger(
                    conditions=subp.AtLeast(4),
                    actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
                )

        return memio.f_bread_epd(epd, subp)
