# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import struct
from collections.abc import Iterator, Sequence
from typing import Literal, TypeAlias, overload

from typing_extensions import Self

from ... import utils as ut
from ...bindings._rust import allocator as alc
from ...localize import _
from ..allocator import ConstExpr, IsConstExpr
from ..allocator.payload import ObjCollector
from ..eudobj import EUDObject
from .action import Action
from .condition import Condition
from .triggerscope import NextTrigger, _register_trigger

# Trigger counter thing

_trg_counter = 0


def GetTriggerCounter() -> int:  # noqa: N802
    return _trg_counter


# Aux


@overload
def Disabled(arg: Condition) -> Condition:
    ...


@overload
def Disabled(arg: Action) -> Action:
    ...


def Disabled(arg: Condition | Action) -> Condition | Action:  # noqa: N802
    """Disable condition or action"""
    arg.disable()
    return arg


Trigger: TypeAlias = ConstExpr | int | None
_Condition: TypeAlias = Condition | bool | Sequence[Condition | bool]
_Action: TypeAlias = Action | Sequence[Action]


class RawTrigger(EUDObject):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    @overload
    def __init__(
        self,
        prevptr: Trigger = None,
        nextptr: Trigger = None,
        conditions: _Condition | None = None,
        actions: _Action | None = None,
        *,
        preserved: bool = True,
        trigSection: None = None,  # noqa: N803
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        prevptr: Trigger = None,
        nextptr: Trigger = None,
        conditions: None = None,
        actions: None = None,
        *,
        preserved: Literal[True] = True,
        trigSection: bytes,  # noqa: N803
    ) -> None:
        ...

    def __init__(
        self,
        prevptr: Trigger = None,
        nextptr: Trigger = None,
        conditions: _Condition | None = None,
        actions: _Action | None = None,
        *,
        preserved: bool = True,
        trigSection: bytes | None = None,  # noqa: N803
    ) -> None:
        super().__init__()

        # Uses normal condition/action initialization
        if trigSection is None:
            # Normalize conditions/actions
            _conditions: Iterator[Condition]
            if conditions is None:
                _conditions = iter(())
            else:
                _conditions = ut.FlattenIter(conditions)

            _actions: Iterator[Action]
            if actions is None:
                _actions = iter(())
            else:
                _actions = ut.FlattenIter(actions)

            # Register condition/actions to trigger
            __conditions = []
            for i, cond in enumerate(_conditions):
                if i >= 16:
                    raise ut.EPError(_("Too many conditions"))
                if isinstance(cond, bool):
                    if cond:
                        cond = Condition(0, 0, 0, 0, 0, 22, 0, 0)  # Always
                    else:
                        cond = Condition(0, 0, 0, 0, 0, 23, 0, 0)  # Never
                cond.CheckArgs(i)
                __conditions.append(cond)

            __actions = []
            for i, act in enumerate(_actions):
                if i >= 64:
                    raise ut.EPError(_("Too many actions"))
                act.CheckArgs(i)
                __actions.append(act)

            for i, cond in enumerate(__conditions):
                cond.SetParentTrigger(self, i)
            for i, act in enumerate(__actions):
                act.SetParentTrigger(self, i)

            self._conditions = __conditions
            self._actions = __actions
            self._flags = 4 if preserved else 0

        # Uses trigger segment for initialization
        # NOTE : player information is lost inside eudplib.
        else:
            self._conditions, self._actions = [], []
            for i in range(16):
                condtype = trigSection[i * 20 + 15]
                if condtype == 22:
                    continue  # ignore Always, no worry disable/enable
                elif condtype >= 1:
                    condition = struct.unpack_from("<IIIHBBBBH", trigSection, i * 20)
                    self._conditions.append(
                        Condition(*condition[:8], eudx=condition[8])
                    )
            self._flags = trigSection[320 + 2048] & 5
            for i in range(64):
                acttype = trigSection[320 + i * 32 + 26]
                if acttype == 47:  # Comment
                    continue
                elif acttype >= 1:
                    action = struct.unpack_from(
                        "<IIIIIIHBBBBH", trigSection, 320 + i * 32
                    )
                    self._actions.append(Action(*action[:10], eudx=action[11]))

        if nextptr is not None and not IsConstExpr(nextptr):
            raise ut.EPError(_("nextptr should be ConstExpr"))

        # Register trigger to global table
        global _trg_counter
        _trg_counter += 1
        _register_trigger(self)  # This should be called before (1)

        # Set linked list pointers
        if prevptr is None:
            prevptr = 0
        if nextptr is None:
            nextptr = NextTrigger()  # (1)

        self._prevptr = prevptr
        self._nextptr = nextptr

    @property
    def preserved(self) -> bool:
        return bool(self._flags & 4)

    @preserved.setter
    def preserved(self, preserved: bool) -> None:
        if preserved:
            self._flags |= 4
        else:
            self._flags &= ~4

    def GetDataSize(self) -> int:  # noqa: N802
        return 2408

    def CollectDependency(self, pbuffer: ObjCollector) -> None:  # noqa: N802
        pbuffer.WriteDword(self._prevptr)
        pbuffer.WriteDword(self._nextptr)

        for cond in self._conditions:
            cond.CollectDependency(pbuffer)
        for act in self._actions:
            act.CollectDependency(pbuffer)

    # RawTrigger.WritePayload is overridden in Allocating and Writing phase
    # (See eudplib.core.allocator.payload.CreatePayload)
    def _allocate_trigger(self, pbuffer: alc.ObjAllocator) -> None:
        pbuffer._write_trigger(len(self._conditions), len(self._actions))

    def _write_trigger(self, pbuffer: alc.PayloadBuffer) -> None:
        pbuffer._write_trigger(
            self._prevptr,
            self._nextptr,
            # FIXME: Change Condition and Action to #[pyclass]
            (cond.fields for cond in self._conditions),
            (act.fields for act in self._actions),
            self._flags,
        )
