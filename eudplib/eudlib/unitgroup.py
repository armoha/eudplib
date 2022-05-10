from eudplib import *


def f_simpleprint(arg):
    pass


class Zerglings:
    def __init__(self, capacity, max_pending):
        self.max_pending = max_pending
        self.unit_group = UnitGroup(capacity)
        self.player_bits = (15, 30, 31)
        self.xy = EUDVariable()
        self._pop = Forward()
        self.queue = EUDVArray(max_pending)(dest=self.xy, nextptr=self._pop)
        self.head = Forward()
        self.is_empty = Memory(self.head, Exactly, self.queue)

    def loop(self):
        for unit in self.unit_group:
            with unit:
                # 저글링이 죽으면 실행할 트리거
                tail = SetMemory(self.queue + 348, SetTo, 0)
                set_player = SetMemory(tail + 20, Add, 0)
                for i, bit in enumerate(self.player_bits):
                    Trigger(
                        DeathsX(CurrentPlayer, AtLeast, 1, 0, 1 << i),
                        SetMemory(set_player + 20, Add, 1 << bit),
                    )
                unit.move_cp(0x28 // 4)
                f_maskread_cp(0, 0x1FFF1FFF, ret=[EPD(tail) + 5])
                DoActions(
                    set_player,
                    tail,
                    SetMemory(set_player + 20, SetTo, 0),
                    SetMemory(tail + 16, Add, 18),
                    SetMemory(self.is_empty + 8, Add, 72),
                )
                Trigger(
                    Memory(
                        tail + 16, AtLeast, EPD(self.queue) + 87 + 18 * self.max_pending
                    ),
                    [
                        SetMemory(tail + 16, SetTo, EPD(self.queue) + 87),
                        SetMemory(self.is_empty + 8, SetTo, self.queue),
                    ],
                )
                f_simpleprint("글링 사망")
            # 저글링이 살아있으면 실행할 트리거

    def popleft(self, counter, actions):
        check_player = DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF)
        check_position = [
            DeathsX(CurrentPlayer, AtLeast, 0, 0, 0x3FFF),
            DeathsX(CurrentPlayer, AtLeast, 0, 0, 0x3FFF0000),
            DeathsX(CurrentPlayer, AtMost, 0, 0, 0x3FFF),
            DeathsX(CurrentPlayer, AtMost, 0, 0, 0x3FFF0000),
        ]
        set_cp = SetMemory(0x6509B0, SetTo, EPD(counter))
        branch, branch_end = Forward(), Forward()
        init_branch = SetMemory(branch + 4, SetTo, self.queue)
        self.head << init_branch + 20
        DoActions([init_branch] + actions)
        branch << RawTrigger(
            nextptr=self.queue,
            conditions=self.is_empty,
            actions=[
                SetMemory(check_player + 8, SetTo, 255),
                SetNextPtr(branch, branch_end),
            ],
        )
        self._pop << RawTrigger(
            actions=[
                SetResources(AllPlayers, Add, 1, Gas),
                SetMemory(check_player + 8, SetTo, 0),
                SetMemory(self.head, Add, 72),
                SetMemory(set_cp + 20, SetTo, EPD(counter)),
            ]
        )
        Trigger(
            Memory(self.head, AtLeast, self.queue + 72 * self.max_pending),
            SetMemory(self.head, SetTo, self.queue),
        )
        for i, bit in enumerate(self.player_bits):
            Trigger(
                self.xy.AtLeastX(1, 1 << bit),
                [
                    SetMemory(check_player + 8, Add, 1 << i),
                    SetMemory(set_cp + 20, Add, 1 << i),
                ],
            )
        self.y = EUDXVariable(0, SetTo, 0, 0x3FFF0000)
        VProc(
            [self.xy, self.y],
            [
                self.xy.SetDest(self.y),
                self.xy.SetMask(0x3FFF0000),
                self.y.SetDest(EPD(check_position[1]) + 2),
            ],
        )
        VProc(
            [self.xy, self.y],
            [
                SetMemory(check_position[1] + 8, Subtract, 128 << 16),
                self.xy.SetDest(EPD(check_position[0]) + 2),
                self.xy.SetMask(0x3FFF),
                self.y.SetDest(EPD(check_position[3]) + 2),
            ],
        )
        VProc(
            self.xy,
            [
                SetMemory(check_position[0] + 8, Subtract, 128),
                SetMemory(check_position[3] + 8, Add, 128 << 16),
                self.xy.SetDest(EPD(check_position[2]) + 2),
            ],
        )
        f_dwadd_epd(EPD(check_position[2]) + 2, 128)
        branch_end << NextTrigger()
        return check_player, check_position, set_cp


def UnsafeWhileNot():
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
    def __init__(self, capacity):
        self.capacity = capacity
        self.loopvar = EUDVariable(EPD(0x6509B0), SetTo, 0)
        self.varray = EUDVArray(capacity)(
            dest=self.loopvar, nextptr=self.loopvar.GetVTable()
        )
        self.trg = EUDVariable(self.varray + 72 * capacity)
        self.pos = EUDVariable(EPD(self.varray) + 87 + 18 * capacity)

    def add(self, unit_epd):
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

    def __iter__(self, on_death=None):
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

        if UnsafeWhileNot()(
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
            yield CpHelper(0x4C // 4, reset_cp, remove)
            EUDSetContinuePoint()
            DoActions(SetMemory(loopstart, Add, 72), SetMemory(pos, Add, 18))
        EUDEndWhile()


class CpHelper:
    def __init__(self, offset, resetf, removef):
        self.offset = offset
        self._reset = resetf
        self.remove = removef

    def __enter__(self):
        EUDIf()(DeathsX(CurrentPlayer, Exactly, 0, 0, 0xFF00))

    def __exit__(self, exc_type, exc_value, tb):
        self.remove()
        EUDEndIf()
        self.offset = 19

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
