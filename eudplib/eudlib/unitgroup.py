#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ..core import (
    Add,
    AtLeast,
    AtMost,
    ConstExpr,
    CurrentPlayer,
    Deaths,
    DeathsX,
    EUDVariable,
    EUDVArray,
    Exactly,
    Forward,
    IsEUDVariable,
    Memory,
    NextTrigger,
    PopTriggerScope,
    PushTriggerScope,
    RawTrigger,
    SeqCompute,
    SetDeathsX,
    SetMemory,
    SetNextPtr,
    SetNextTrigger,
    SetTo,
    Subtract,
    VProc,
)
from ..ctrlstru import DoActions, EUDEndWhile, EUDSetContinuePoint
from ..ctrlstru.loopblock import _UnsafeWhileNot
from ..utils import EPD, EUDCreateBlock, EUDPeekBlock, ep_assert

_assign_helper = EUDVariable()


class UnitGroup:
    """Loop-efficient CUnit EPD collection

    ```js
    // epScript example

    // UnitGroup Declaration
    const zerglings = UnitGroup(1000);
    // max capacity = 1000, will use CPTrick

    // Register Unit
    zerglings.add(epd);

    // Loop UnitGroup
    foreach(unit : zerglings.cploop) {
        // Run Triggers on **any** zerglings (alive or dead)
        foreach(dead : unit.dying) {
            // Run Triggers on dead zerglings
        }  // <- dead zergling will be removed at end of *dying* block
        // Run Triggers on alive zerglings
    }

    // example usage
    function afterTriggerExec() {
        const zerglings = UnitGroup(1000);
        foreach(ptr, epd : EUDLoopNewUnit()) {
            const cunit = EPDCUnitMap(epd);
            if (cunit.unitId = $U("Zerg Zergling")) {
                zerglings.add(epd);
            }
        }
        foreach(unit : zerglings.cploop) {
            foreach(dead : unit.dying) {
                // spawn Infested Terran when zergling dies
                dead.move_cp(0x4C / 4);  // Owner
                const owner = bread_cp(0, 0);
                dead.move_cp(0x28 / 4);  // Unit Position
                const x, y = posread_cp(0);

                setloc("loc", x, y);
                CreateUnit(1, "Infested Terran", "loc", owner);
            }
        }
    }
    ```
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.loopvar = EUDVariable(EPD(0x6509B0), SetTo, 0)
        varray = EUDVArray(capacity)(dest=self.loopvar, nextptr=self.loopvar.GetVTable())
        self.varray = varray
        self.trg = EUDVariable(self.varray + 72 * capacity)
        self.pos = EUDVariable(EPD(self.varray) + 87 + 18 * capacity)

        class _CPLoop:
            def __init__(self, parent):
                self._parent = parent

            def __iter__(self):
                loopstart, pos, check_death = Forward(), Forward(), Forward()
                trg, tpos, loopvar = (
                    self._parent.trg,
                    self._parent.pos,
                    self._parent.loopvar,
                )

                VProc(
                    [trg, tpos],
                    [
                        trg.SetDest(EPD(loopstart)),
                        tpos.SetDest(EPD(pos)),
                        SetNextPtr(loopvar.GetVTable(), check_death),
                    ],
                )

                def reset_cp():
                    PushTriggerScope()
                    reset_nextptr = RawTrigger(
                        actions=SetNextPtr(loopvar.GetVTable(), check_death)
                    )
                    PopTriggerScope()
                    nextptr = Forward()
                    RawTrigger(
                        nextptr=loopvar.GetVTable(),
                        actions=[
                            SetNextPtr(loopvar.GetVTable(), reset_nextptr),
                            SetNextPtr(reset_nextptr, nextptr),
                        ],
                    )
                    nextptr << NextTrigger()

                if _UnsafeWhileNot()(Memory(loopstart, AtLeast, varray + 72 * capacity)):
                    block = EUDPeekBlock("whileblock")[1]
                    PushTriggerScope()  # remove entry
                    remove_end = Forward()
                    remove_start = RawTrigger(
                        nextptr=trg.GetVTable(),
                        actions=[
                            trg.SetDest(EPD(trg.GetVTable()) + 1),
                            SetNextPtr(loopvar.GetVTable(), remove_end),
                            loopvar.SetDest(0),  # pos가 이 액션의 값 칸
                        ],
                    )
                    pos << remove_start + 328 + 32 * 2 + 20
                    remove_end << RawTrigger(
                        actions=[
                            trg.AddNumber(72),
                            tpos.AddNumber(18),
                            loopvar.SetDest(EPD(0x6509B0)),
                            SetNextPtr(loopvar.GetVTable(), check_death),
                        ]
                    )
                    SetNextTrigger(block["contpoint"])
                    PopTriggerScope()

                    loopstart << block["loopstart"] + 4
                    check_death << NextTrigger()

                    def get_epd():
                        ret = EUDVariable()
                        VProc(loopvar, loopvar.SetDest(ret))
                        DoActions(
                            SetNextPtr(loopvar.GetVTable(), check_death),
                            loopvar.SetDest(EPD(0x6509B0)),
                            ret.SubtractNumber(19),
                        )
                        return ret

                    # EUDIf()(DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF00)):
                    yield _CpHelper(0x4C // 4, reset_cp, remove_start, get_epd)
                    EUDSetContinuePoint()
                    DoActions(SetMemory(loopstart, Add, 72), SetMemory(pos, Add, 18))
                EUDEndWhile()
                ep_assert(pos.IsSet(), "unit.dying must be added")

        self.cploop = _CPLoop(self)

    def add(self, unit_epd):
        if IsEUDVariable(unit_epd):
            # Occupy 2T, Run 4T 10A
            SeqCompute(
                [
                    (self.trg, Subtract, 72),
                    (self.pos, Subtract, 18),
                    (unit_epd, Add, 0x4C // 4),
                    (EPD(unit_epd._varact) + 6, SetTo, 0x072D0000),
                    (EPD(unit_epd.getDestAddr()), None, self.pos),
                    (None, None, unit_epd),
                ]
            )
            unit_epd -= 0x4C // 4
        else:
            # Occupy 1T, Run 4T 9A
            global _assign_helper
            SeqCompute(
                [
                    (self.trg, Subtract, 72),
                    (self.pos, Subtract, 18),
                    (_assign_helper, SetTo, unit_epd + 0x4C // 4),
                    (EPD(_assign_helper.getDestAddr()), None, self.pos),
                    (None, None, _assign_helper),
                ]
            )


# TODO: Add EPDCUnitMap-like convenient methods
class _CpHelper:
    def __init__(self, offset, resetf, remove, epdf):
        self.offset = offset
        self._reset = resetf
        self._remove_start = remove
        self.get_epd = epdf

        class Dying:
            def __iter__(nonself):
                dying_end, check_death, dying_block = Forward(), Forward(), Forward()
                RawTrigger(
                    actions=[
                        self.move_cp(0x08 // 4, action=True),
                        SetNextPtr(check_death, dying_end),
                    ]
                )
                RawTrigger(
                    conditions=Deaths(CurrentPlayer, Exactly, 0, 0),
                    actions=[
                        self.move_cp(0x4C // 4, action=True),
                        SetDeathsX(CurrentPlayer, SetTo, 0, 0, 0xFF00),
                        self.move_cp(0x08 // 4, action=True),
                    ],
                )
                self.move_cp(0x4C // 4)
                check_death << RawTrigger(
                    nextptr=dying_end,
                    conditions=DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF00),
                    actions=SetNextPtr(check_death, dying_block),
                )
                dying_block << NextTrigger()
                yield self
                self.remove()
                self.offset = 19
                dying_end << NextTrigger()

        self.dying = Dying()

    def remove(self):
        SetNextTrigger(self._remove_start)

    @property  # read-only
    def epd(self) -> EUDVariable:
        return self.get_epd()

    def set_cp(self, offset, *, action=False):
        self._reset()
        self.offset = 19
        return self.move_cp(offset, action=False)

    def move_cp(self, offset, *, action=False):
        try:
            if offset > self.offset:
                mod, val = Add, offset - self.offset
            elif offset < self.offset:
                mod, val = Subtract, self.offset - offset
        except TypeError as e:
            if isinstance(offset, ConstExpr) and isinstance(self.offset, int):
                mod, val = Add, offset - self.offset
            elif isinstance(offset, int) and isinstance(self.offset, ConstExpr):
                mod, val = Subtract, self.offset - offset
            elif (
                isinstance(offset, ConstExpr)
                and isinstance(self.offset, ConstExpr)
                and offset.baseobj is self.offset.baseobj
                and offset.rlocmode == self.offset.rlocmode
            ):
                if offset.offset > self.offset.offset:
                    mod, val = Add, offset.offset - self.offset.offset
                elif offset.offset < self.offset.offset:
                    mod, val = Subtract, self.offset.offset - offset.offset
            else:
                raise e
        self.offset = offset
        try:
            if action:
                return SetMemory(0x6509B0, mod, val)
            else:
                DoActions(SetMemory(0x6509B0, mod, val))
        except NameError:
            pass
