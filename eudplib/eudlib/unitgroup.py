from ..core import Forward, NextTrigger, RawTrigger, SetNextPtr, EUDVariable, EUDVArray, SetTo, SeqCompute, Subtract, Add, AtLeast, VProc, PushTriggerScope, PopTriggerScope, Memory, SetNextTrigger, SetMemory, CurrentPlayer, ConstExpr, DeathsX, Exactly, IsEUDVariable
from ..ctrlstru import CtrlStruOpener, DoActions, EUDSetContinuePoint, EUDEndWhile, EUDIf, EUDEndIf
from ..utils import EPD, EUDCreateBlock, EUDPeekBlock, ep_assert

_assign_helper = EUDVariable()


def _UnsafeWhileNot():
    def _header():
        block = {
            "loopstart": NextTrigger(),
            "loopend": Forward(),
            "contpoint": Forward(),
            "conditional": True,
        }

        EUDCreateBlock("whileblock", block)

    def _footer(conditions):
        block = EUDPeekBlock("whileblock")[1]
        RawTrigger(
            conditions=conditions,
            actions=SetNextPtr(block["loopstart"], block["loopend"]),
        )
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


class UnitGroup:
    """Loop-efficient CUnit EPD collection

    ```js
    // epScript example

    // UnitGroup Declaration
    const zerglings = UnitGroup(1000, CurrentPlayer);
    // max capacity = 1000, will use CPTrick

    // Register Unit
    zerglings.add(epd);

    // Loop UnitGroup
    foreach(unit : zerglings) {
        // Run Triggers on **any** zerglings (alive or dead)
        foreach(dead : unit.dying) {
            // Run Triggers on dead zerglings
        }  // <- dead zergling will be removed at end of *dying* block
        // Run Triggers on alive zerglings
    }

    // example usage
    function afterTriggerExec() {
        const zerglings = UnitGroup(1000, CurrentPlayer);
        foreach(ptr, epd : EUDLoopNewUnit()) {
            const cunit = EPDCUnitMap(epd);
            if (cunit.unitId = $U("Zerg Zergling")) {
                zerglings.add(epd);
            }
        }
        foreach(unit : zerglings) {
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
    def __init__(self, capacity, target):
        ep_assert(target == CurrentPlayer, "Currently UnitGroup targetvar only supports CurrentPlayer")
        self._target = target
        self.capacity = capacity
        self.loopvar = EUDVariable(EPD(0x6509B0), SetTo, 0)
        self.varray = EUDVArray(capacity)(
            dest=self.loopvar, nextptr=self.loopvar.GetVTable()
        )
        self.trg = EUDVariable(self.varray + 72 * capacity)
        self.pos = EUDVariable(EPD(self.varray) + 87 + 18 * capacity)

    def add(self, unit_epd):
        if IsEUDVariable(unit_epd):
            # Occupy 2T, Run 4T 10A
            SeqCompute(
                [
                    (self.trg, Subtract, 72),
                    (self.pos, Subtract, 18),
                    (unit_epd, Add, 0x4C // 4),
                    (EPD(unit_epd.getDestAddr()), None, self.pos),
                    (None, SetTo, unit_epd),
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
                    (None, SetTo, _assign_helper),
                ]
            )

    def __iter__(self):
        loopstart, pos, check_death = Forward(), Forward(), Forward()
        VProc(
            [self.trg, self.pos],
            [
                self.trg.SetDest(EPD(loopstart)),
                self.pos.SetDest(EPD(pos)),
                SetNextPtr(self.loopvar.GetVTable(), check_death),
            ],
        )

        def reset_cp():
            PushTriggerScope()
            reset_nextptr = RawTrigger(
                actions=SetNextPtr(self.loopvar.GetVTable(), check_death)
            )
            PopTriggerScope()
            nextptr = Forward()
            RawTrigger(
                nextptr=self.loopvar.GetVTable(),
                actions=[
                    SetNextPtr(self.loopvar.GetVTable(), reset_nextptr),
                    SetNextPtr(reset_nextptr, nextptr),
                ],
            )
            nextptr << NextTrigger()

        if _UnsafeWhileNot()(
            Memory(loopstart, AtLeast, self.varray + 72 * self.capacity)
        ):
            block = EUDPeekBlock("whileblock")[1]
            loopstart << block["loopstart"] + 4
            check_death << NextTrigger()

            def remove():
                remove_end = Forward()
                remove_start = RawTrigger(
                    nextptr=self.trg.GetVTable(),
                    actions=[
                        self.trg.SetDest(EPD(self.trg.GetVTable()) + 1),
                        SetNextPtr(self.loopvar.GetVTable(), remove_end),
                        self.loopvar.SetDest(0),  # pos가 이 액션의 값 칸
                    ],
                )
                pos << remove_start + 328 + 32 * 2 + 20
                remove_end << RawTrigger(
                    actions=[
                        self.trg.AddNumber(72),
                        self.pos.AddNumber(18),
                        self.loopvar.SetDest(EPD(0x6509B0)),
                        SetNextPtr(self.loopvar.GetVTable(), check_death),
                    ]
                )
                SetNextTrigger(block["contpoint"])

            # EUDIf()(DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF00)):
            yield _CpHelper(0x4C // 4, reset_cp, remove)
            EUDSetContinuePoint()
            DoActions(SetMemory(loopstart, Add, 72), SetMemory(pos, Add, 18))
        EUDEndWhile()
        ep_assert(pos.IsSet(), "unit.dying must be added")


# TODO: Add EPDCUnitMap-like convenient methods
class _CpHelper:
    def __init__(self, offset, resetf, removef):
        self.offset = offset
        self._reset = resetf
        self.remove = removef
        class Dying:
            def __iter__(nonself):
                self.move_cp(0x4C // 4)
                if EUDIf()(DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF00)):
                    yield self
                    self.remove()
                EUDEndIf()
                self.offset = 19
        self.dying = Dying()

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
