#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

import sys
import traceback
from collections.abc import Iterator, Sequence
from itertools import pairwise
from typing import TYPE_CHECKING, Any, TypeGuard, TypeVar, overload

from typing_extensions import Self

from ...localize import _
from ...utils import (
    EPD,
    EPError,
    ExprProxy,
    FlattenList,
    List2Assignable,
    ep_assert,
    ep_warn,
    unProxy,
)
from .. import rawtrigger as bt
from ..allocator import ConstExpr, Forward
from .vbase import VariableBase
from .vbuf import get_current_custom_varbuffer, get_current_varbuffer

if TYPE_CHECKING:
    from ..rawtrigger.constenc import Dword, TrgModifier


_is_rvalue_strict = False
T = TypeVar("T", int, ConstExpr, ExprProxy[int] | ExprProxy[ConstExpr])


def EP_SetRValueStrictMode(mode: bool) -> None:  # noqa: N802
    global _is_rvalue_strict
    _is_rvalue_strict = mode


def process_dest(dest):
    epd = unProxy(dest)
    if isinstance(epd, VariableBase):
        epd.checkNonRValue()
        return EPD(epd.getValueAddr())
    return epd


def _is_rvalue(obj: object, refcount: int = 4) -> bool:
    if isinstance(obj, EUDVariable) and sys.getrefcount(obj) != refcount:
        return False
    if isinstance(obj, ExprProxy) and not _is_rvalue(obj.getValue(), refcount + 1):
        return False
    return True


if sys.version_info >= (3, 11):
    _initial_refcount = 2
else:
    _initial_refcount = 3


def _yield_and_check_rvalue(
    obj: Any, refcount: int = _initial_refcount, is_rvalue: bool = True
) -> Iterator[tuple[Any, bool]]:
    is_rvalue &= sys.getrefcount(obj) == refcount
    if isinstance(obj, ExprProxy):
        yield from _yield_and_check_rvalue(obj.getValue(), 3, is_rvalue)
    elif isinstance(obj, EUDVariable):
        yield obj, is_rvalue
    elif isinstance(obj, (bytes, str)) or hasattr(obj, "dont_flatten"):  # noqa: UP038
        yield obj, False
    else:
        try:
            for subobj in obj:
                yield from _yield_and_check_rvalue(subobj, 4, is_rvalue)
        except TypeError:  # obj is not iterable
            yield obj, False


# Unused variable don't need to be allocated.
class VariableTriggerForward(ConstExpr):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(self, initval) -> None:
        super().__init__()
        self._initval = initval

    def Evaluate(self):  # noqa: N802
        if isinstance(self._initval, tuple):
            evb = get_current_custom_varbuffer()
        else:
            evb = get_current_varbuffer()
        try:
            return evb._vdict[self].Evaluate()
        except KeyError:
            vt = evb.create_vartrigger(self, self._initval)
            return vt.Evaluate()


class EUDVariable(VariableBase):
    """Full variable."""

    _addor: EUDVariable
    __slots__ = ("_vartrigger", "_varact", "_rvalue")

    @overload
    def __init__(
        self,
        initval_or_epd: int | ConstExpr = 0,
        modifier: None = None,
        initval: None = None,
        /,
        *,
        nextptr: None = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        initval_or_epd: int | ConstExpr,
        modifier: TrgModifier,
        initval: int | ConstExpr,
        /,
        *,
        nextptr: ConstExpr | None = None,
    ) -> None:
        ...

    def __init__(
        self, initval_or_epd=0, modifier=None, initval=None, /, *, nextptr=None
    ) -> None:
        if modifier is None and initval is None and nextptr is None:
            initial_pair = initval_or_epd
        else:
            ep_assert(modifier and initval is not None)
            if nextptr is None:
                nextptr = 0
            # bitmask, player, #, modifier, nextptr
            initial_pair = (
                0xFFFFFFFF,
                process_dest(initval_or_epd),
                initval,
                ((bt.EncodeModifier(modifier) & 0xFF) << 24) | 0x2D0000,
                nextptr,
            )
        self._vartrigger = VariableTriggerForward(initial_pair)
        self._varact: ConstExpr = self._vartrigger + (8 + 320)  # type: ignore[assignment]
        self._rvalue = False

    def GetVTable(self) -> ConstExpr:  # noqa: N802
        return self._vartrigger

    def getMaskAddr(self) -> ConstExpr:  # noqa: N802
        return self._varact

    def getDestAddr(self) -> ConstExpr:  # noqa: N802
        return self._varact + 16  # type: ignore[return-value]

    def getValueAddr(self) -> ConstExpr:  # noqa: N802
        return self._varact + 20  # type: ignore[return-value]

    def __hash__(self) -> int:
        return id(self)

    # -------
    def makeL(self) -> EUDVariable:  # noqa: N802
        self._rvalue = False
        return self

    def makeR(self) -> EUDVariable:  # noqa: N802
        self._rvalue = True
        return self

    def checkNonRValue(self) -> None:  # noqa: N802
        if _is_rvalue_strict and self._rvalue:
            raise EPError(_("Trying to modify value of r-value variable"))

    # -------

    def SetMask(self, value: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemory(self.getMaskAddr(), bt.SetTo, value)

    def AddMask(self, value: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemory(self.getMaskAddr(), bt.Add, value)

    def SubtractMask(self, value: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemory(self.getMaskAddr(), bt.Subtract, value)

    # -------

    def SetMaskX(self, value: Dword, mask: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemoryX(self.getMaskAddr(), bt.SetTo, value, mask)

    def AddMaskX(self, value: Dword, mask: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemoryX(self.getMaskAddr(), bt.Add, value, mask)

    def SubtractMaskX(self, value: Dword, mask: Dword) -> bt.Action:  # noqa: N802
        return bt.SetMemoryX(self.getMaskAddr(), bt.Subtract, value, mask)

    # -------

    def MaskAtLeast(self, value: Dword) -> bt.Condition:  # noqa: N802
        return bt.Memory(self.getMaskAddr(), bt.AtLeast, value)

    def MaskAtMost(self, value: Dword) -> bt.Condition:  # noqa: N802
        return bt.Memory(self.getMaskAddr(), bt.AtMost, value)

    def MaskExactly(self, value: Dword) -> bt.Condition:  # noqa: N802
        return bt.Memory(self.getMaskAddr(), bt.Exactly, value)

    # -------

    def MaskAtLeastX(self, value: Dword, mask: Dword) -> bt.Condition:  # noqa: N802
        return bt.MemoryX(self.getMaskAddr(), bt.AtLeast, value, mask)

    def MaskAtMostX(self, value: Dword, mask: Dword) -> bt.Condition:  # noqa: N802
        return bt.MemoryX(self.getMaskAddr(), bt.AtMost, value, mask)

    def MaskExactlyX(self, value: Dword, mask: Dword) -> bt.Condition:  # noqa: N802
        return bt.MemoryX(self.getMaskAddr(), bt.Exactly, value, mask)

    # -------

    def SetDest(self, dest) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.SetTo, dest)

    def AddDest(self, dest) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.Add, dest)

    def SubtractDest(self, dest) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.Subtract, dest)

    # -------

    def SetDestX(self, dest, mask: Dword) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.SetTo, dest, mask)

    def AddDestX(self, dest, mask: Dword) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.Add, dest, mask)

    def SubtractDestX(self, dest, mask: Dword) -> bt.Action:  # noqa: N802
        dest = process_dest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.Subtract, dest, mask)

    # -------

    def SetModifier(self, modifier) -> bt.Action:  # noqa: N802
        ep_assert(
            modifier is bt.SetTo or modifier is bt.Add or modifier is bt.Subtract,
            _("Unexpected modifier {}").format(modifier),
        )
        modifier = bt.EncodeModifier(modifier) << 24
        return bt.SetDeathsX(
            EPD(self._varact + 24), bt.SetTo, modifier, 0, 0xFF000000
        )

    # -------

    def QueueAssignTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.SetTo)]

    def QueueAddTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.Add)]

    def QueueSubtractTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.Subtract)]

    # -------

    def Assign(self, other: Dword) -> EUDVariable:  # noqa: N802
        self.checkNonRValue()
        SeqCompute(((self, bt.SetTo, other),))
        return self

    def __lshift__(self, other: Dword) -> EUDVariable:
        return self.Assign(other)

    def __iadd__(self, other: Dword) -> EUDVariable:
        SeqCompute(((self, bt.Add, other),))
        return self

    def __isub__(self, other: Dword) -> EUDVariable:
        if isinstance(other, int):
            self.__iadd__(-other)  # 1A
        else:
            try:
                addor = EUDVariable._addor
            except AttributeError:
                addor = EUDVariable(0, bt.Add, 0)
                EUDVariable._addor = addor
            SeqCompute(
                [  # (self + 1) + (~0 - other)
                    (self, bt.Add, 1),
                    (addor, bt.SetTo, 0xFFFFFFFF),
                    (addor, bt.Subtract, other),
                    (self, None, addor),
                ]
            )
        return self

    # -------

    def __add__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iadd__(other)
        if IsEUDVariable(other) and _is_rvalue(other):
            return other.__iadd__(self)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, other), (t, bt.Add, self)])
        return t.makeR()

    def __radd__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iadd__(other)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, other), (t, bt.Add, self)])
        return t.makeR()

    def __sub__(self, other: Dword) -> EUDVariable:
        if IsEUDVariable(other) and _is_rvalue(other):
            rvalue_strict = _is_rvalue_strict
            if rvalue_strict:
                EP_SetRValueStrictMode(False)
            VProc(
                self,  # -other += self
                [
                    other.AddNumberX(0xFFFFFFFF, 0x55555555),
                    other.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    other.AddNumber(1),
                    self.QueueAddTo(other),
                ],
            )  # 1T 7A, executes 2T 8A
            if rvalue_strict:
                EP_SetRValueStrictMode(True)
            return other
        if _is_rvalue(self):
            return self.__isub__(other)
        t = EUDVariable()
        # FIXME: unsupported EUD error after EUDStruct.free() with IsConstExpr
        if isinstance(other, int):
            SeqCompute(
                [
                    (t, bt.SetTo, -other),
                    (t, bt.Add, self),
                ]
            )
        else:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, other),
                    (t, bt.Add, 1),
                    (t, bt.Add, self),
                ]
            )
        return t.makeR()

    def __rsub__(self, other: Dword) -> EUDVariable:
        is_eudvariable = IsEUDVariable(other)
        if _is_rvalue(self) and not is_eudvariable:
            bt.RawTrigger(  # -self += other
                actions=[
                    self.AddNumberX(0xFFFFFFFF, 0x55555555),
                    self.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    self.AddNumber(other + 1),
                ]
            )
            return self
        t = EUDVariable()
        if is_eudvariable:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, self),
                    (t, bt.Add, 1),
                    (t, bt.Add, other),
                ]
            )
        else:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, self),
                    (t, bt.Add, other + 1),
                ]
            )
        return t.makeR()

    def __neg__(self) -> EUDVariable:
        if _is_rvalue(self):
            return self.ineg()
        return (0 - self).makeR()

    def __invert__(self) -> EUDVariable:
        if _is_rvalue(self):
            return self.iinvert()
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, 0xFFFFFFFF), (t, bt.Subtract, self)])
        return t.makeR()

    # -------

    def __ior__(self, other: Dword) -> EUDVariable:
        if IsEUDVariable(other):
            write = self.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(EPD(write), bt.SetTo, other)])
            bt.RawTrigger(actions=write)  # 1T 5A
        else:
            super().__ior__(other)  # 1A
        return self

    def __iand__(self, other: Dword) -> EUDVariable:
        if IsEUDVariable(other):
            write = self.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (EPD(write), bt.Subtract, other),
                ]
            )
            bt.RawTrigger(actions=write)  # 1T 6A
        else:
            super().__iand__(other)  # 1A
        return self

    # -------

    def __and__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iand__(other)
        is_eudvariable = IsEUDVariable(other)
        if is_eudvariable and _is_rvalue(other):
            return other.__iand__(self)
        t = EUDVariable()
        if is_eudvariable:
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, other),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        else:
            t << self
            t &= other  # 1T 5A
        return t.makeR()

    def __rand__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iand__(other)
        t = EUDVariable()
        if IsEUDVariable(other):
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, other),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        else:
            t << self
            t &= other  # 1T 5A
        return t.makeR()

    def __or__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ior__(other)
        is_eudvariable = IsEUDVariable(other)
        if is_eudvariable and _is_rvalue(other):
            return other.__ior__(self)
        t = EUDVariable()
        if is_eudvariable:
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, other)])
            bt.RawTrigger(actions=write)  # 2T 9A
        else:
            t << self
            t |= other  # 1T 5A
        return t.makeR()

    def __ror__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ior__(other)
        t = EUDVariable()
        if IsEUDVariable(other):
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, other)])
            bt.RawTrigger(actions=write)  # 2T 9A
        else:
            t << self
            t |= other  # 1T 5A
        return t.makeR()

    # -------

    def __ixor__(self, other: Dword) -> EUDVariable:
        if IsEUDVariable(other):
            VProc(
                other,
                [
                    other.SetMask(0x55555555),
                    *other.QueueAddTo(self),
                ],
            )
            VProc(other, other.SetMask(0xAAAAAAAA))  # 3T 8A
            bt.RawTrigger(
                actions=other.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            super().__ixor__(other)  # 2A
        return self

    def __xor__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ixor__(other)
        is_eudvariable = IsEUDVariable(other)
        if is_eudvariable and _is_rvalue(other):
            return other.__ixor__(self)
        t = EUDVariable()
        if is_eudvariable:
            VProc(
                [self, other],
                [
                    other.SetMask(0x55555555),
                    self.QueueAssignTo(t),
                    other.QueueAddTo(t),
                ],
            )
            VProc(other, other.SetMask(0xAAAAAAAA))
            bt.RawTrigger(
                actions=other.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            t << self
            t ^= other
        return t.makeR()

    def __rxor__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ixor__(other)
        t = EUDVariable()
        if IsEUDVariable(other):
            SeqCompute(
                [
                    (EPD(other.getMaskAddr()), bt.SetTo, 0x55555555),
                    (t, bt.SetTo, self),
                    (t, bt.Add, other),
                ]
            )
            VProc(other, other.SetMask(0xAAAAAAAA))
            bt.RawTrigger(
                actions=other.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            t << self
            t ^= other
        return t.makeR()

    # -------

    def __eq__(self, other) -> bt.Condition:  # type: ignore[override]
        try:
            return self.Exactly(other)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            return (self - other).Exactly(0)

    def __ne__(self, other) -> bt.Condition:  # type: ignore[override]
        if isinstance(other, int):
            if other & 0xFFFFFFFF == 0:
                return self.AtLeast(1)
            if other & 0xFFFFFFFF == 0xFFFFFFFF:
                return self.AtMost(0xFFFFFFFE)
        return (self - other).AtLeast(1)

    def __le__(self, other) -> bt.Condition:  # type: ignore[override]
        try:
            return self.AtMost(other)

        except Exception as err:
            ep_warn(_("{}: Patching comparison condition.").format(err))
            traceback.print_stack()
            condition = self.AtMost(0)
            SeqCompute(((EPD(condition) + 2, bt.SetTo, other),))
            return condition

    def __ge__(self, other) -> bt.Condition:  # type: ignore[override]
        try:
            return self.AtLeast(other)

        except Exception as err:
            ep_warn(_("{}: Patching comparison condition.").format(err))
            traceback.print_stack()
            condition = self.AtLeast(0)
            SeqCompute(((EPD(condition) + 2, bt.SetTo, other),))
            return condition

    def __lt__(self, other) -> bt.Condition:  # type: ignore[override]
        other = unProxy(other)
        if isinstance(other, EUDVariable):
            bitmask = Forward()  # u32: Location number or bitmask for the condition
            condition = bt.MemoryEPD(bitmask, bt.AtLeast, 1)
            bitmask << EPD(condition)
            SeqCompute(((bitmask, bt.SetTo, other), (bitmask, bt.Subtract, self)))
            return condition
        if isinstance(other, int) and other <= 0:
            ep_warn(_("No unsigned number can be leq than {}").format(other))
            traceback.print_stack()
            return bt.Never()  # No unsigned number is less than 0
        return self.AtMost(other - 1)

    def __gt__(self, other) -> bt.Condition:  # type: ignore[override]
        other = unProxy(other)
        if isinstance(other, EUDVariable):
            bitmask = Forward()  # u32: Location number or bitmask for the condition
            condition = bt.MemoryEPD(bitmask, bt.AtLeast, 1)
            bitmask << EPD(condition)
            SeqCompute(((bitmask, bt.SetTo, self), (bitmask, bt.Subtract, other)))
            return condition
        if isinstance(other, int) and other >= 0xFFFFFFFF:
            ep_warn(_("No unsigned number can be greater than {}").format(other))
            traceback.print_stack()
            return bt.Never()  # No unsigned number is greater than 0xFFFFFFFF
        return self.AtLeast(other + 1)

    # operator placeholders
    def __mul__(self, a):
        raise NotImplementedError

    def __rmul__(self, a):
        raise NotImplementedError

    def __imul__(self, a):
        raise NotImplementedError

    def __floordiv__(self, a):
        raise NotImplementedError

    def __rfloordiv__(self, a):
        raise NotImplementedError

    def __ifloordiv__(self, a):
        raise NotImplementedError

    def __mod__(self, a):
        raise NotImplementedError

    def __rmod__(self, a):
        raise NotImplementedError

    def __imod__(self, a):
        raise NotImplementedError

    def __ilshift__(self, a):  # type: ignore[misc]
        raise NotImplementedError

    def __irshift__(self, a):
        raise NotImplementedError


def IsEUDVariable(x: object) -> TypeGuard[EUDVariable]:  # noqa: N802
    return isinstance(unProxy(x), EUDVariable)


# ---------


@overload
def VProc(v: EUDVariable, actions) -> bt.RawTrigger:
    ...


@overload
def VProc(
    v: Sequence[EUDVariable], actions
) -> bt.RawTrigger | Sequence[bt.RawTrigger]:
    ...


def VProc(v, actions) -> bt.RawTrigger | Sequence[bt.RawTrigger]:  # noqa: N802
    v = FlattenList(v)
    actions = FlattenList(actions)
    end = Forward()
    triggers = list()

    for cv, nv in pairwise(v):
        actions.append(bt.SetNextPtr(cv.GetVTable(), nv.GetVTable()))
    actions.append(bt.SetNextPtr(v[-1].GetVTable(), end))

    for i in range(0, len(actions), 64):
        triggers.append(bt.RawTrigger(actions=actions[i : i + 64]))
    bt.SetNextTrigger(v[0].GetVTable())
    end << bt.NextTrigger()

    return List2Assignable(triggers)


# From vbuffer.py
def EUDCreateVariables(varn: int):  # noqa: N802
    return List2Assignable([EUDVariable() for _ in range(varn)])


# -------


def _get_computedest(dst):
    try:
        return EPD(dst.getValueAddr())
    except AttributeError:
        return dst


def _seqcompute_sub(assignpairs, _srcdict):
    """
    Subset of SeqCompute with following restrictions

    - Assignment from variable should be after assignment from constant.
    - Total number of actions should be leq than 64
    """

    actionlist = []

    # Collect constant-assigning actions
    const_assigning_index = len(assignpairs)

    for i, assignpair in enumerate(assignpairs):
        dst, mdt, src = assignpair
        if IsEUDVariable(src):
            const_assigning_index = i
            break

    for dst, mdt, src in assignpairs[0:const_assigning_index]:
        dst = _get_computedest(dst)
        actionlist.append(bt.SetDeaths(dst, mdt, src, 0))

    # Only constant-assigning function : skip
    if const_assigning_index == len(assignpairs):
        bt.RawTrigger(actions=actionlist)
        return

    #
    # Rest is for non-constant assigning actions
    #
    nextptr = None  # nextptr for this rawtrigger
    vt_nextptr = None  # what to set for nextptr of current vtable
    last_pairs = None
    non_const_actions = []

    def remove_duplicate_actions() -> None:
        if last_pairs is None:
            return
        src, dst, mdt = last_pairs

        try:
            prev_dst, prev_mdt, prev_nptr = _srcdict[src]
        except KeyError:
            prev_dst, prev_mdt, prev_nptr = None, None, None

        if (dst is not prev_dst) and dst:
            non_const_actions.append(src.SetDest(dst))
        if (mdt is not prev_mdt) and mdt:
            non_const_actions.append(src.SetModifier(mdt))
        if prev_nptr is None or vt_nextptr.expr is not prev_nptr.expr:
            non_const_actions.append(bt.SetNextPtr(src.GetVTable(), vt_nextptr))

        _srcdict[src] = (
            dst if dst else prev_dst,
            mdt if mdt else prev_mdt,
            vt_nextptr,
        )

    for dst, mdt, src in assignpairs[const_assigning_index:]:
        dst = _get_computedest(dst)

        if nextptr is None:
            nextptr = src.GetVTable()
        else:
            vt_nextptr << src.GetVTable()

        remove_duplicate_actions()

        vt_nextptr = Forward()
        last_pairs = src, dst, mdt

    remove_duplicate_actions()
    actionlist.extend(non_const_actions)
    bt.RawTrigger(nextptr=nextptr, actions=actionlist)

    vt_nextptr << bt.NextTrigger()


def SeqCompute(assignpairs):  # noqa: N802
    # We need dependency map while writing assignment pairs
    dstvarset = set()
    srcvarset = set()

    # Record previous dst, mdt for src to optimize duplicate actions
    srcdictsub = {}
    srcdict = {}

    # Sublist of assignments to put in _seqcompute_sub
    subassignpairs = []

    # Is we collecting constant-assigning pairs?
    constcollecting = True

    # Number of expected actions.
    actioncount = 0

    def flush_pairs():
        nonlocal constcollecting, actioncount

        if actioncount == 0:  # Already flushed before
            return

        _seqcompute_sub(subassignpairs, srcdictsub)

        dstvarset.clear()
        srcvarset.clear()
        subassignpairs.clear()
        constcollecting = True
        actioncount = 0

    for assignpair in assignpairs:
        dst, mdt, src = assignpair
        dst = bt.EncodePlayer(unProxy(dst))
        src = unProxy(src)

        # Flush action set before proceeding
        if IsEUDVariable(src):
            if src in srcvarset:
                flush_pairs()
            elif actioncount >= 64 - 3:
                flush_pairs()

            srcvarset.add(src)
            constcollecting = False
            actioncount += 3

            try:
                prev_dst, prev_mdt = srcdict[src]
            except KeyError:
                pass
            else:
                if dst is prev_dst:
                    actioncount -= 1
                if mdt is prev_mdt:
                    actioncount -= 1
            srcdict[src] = dst, mdt

        else:
            if not constcollecting:
                flush_pairs()
            elif actioncount >= 64 - 3:
                flush_pairs()

            actioncount += 1

        subassignpairs.append((dst, mdt, src))
        if IsEUDVariable(dst):
            dstvarset.add(dst)

    flush_pairs()


def NonSeqCompute(assignpairs):  # noqa: N802
    import itertools

    dstvarset = set()
    srcvarset = set()
    constpairs = list()
    varassigndict = dict()

    for assignpair in assignpairs:
        dst, mdt, src = assignpair
        if IsEUDVariable(dst):
            dstvarset.add(dst)
        if IsEUDVariable(src):
            srcvarset.add(src)
            try:
                varassigndict[src].append(assignpair)
            except KeyError:
                varassigndict[src] = [assignpair]
        else:
            constpairs.append(assignpair)

    if len(assignpairs) == len(constpairs):
        SeqCompute(assignpairs)
        return
    ep_assert(dstvarset.isdisjoint(srcvarset), _("dst and src have intersection"))

    varpairlists = list()
    for pairlist in varassigndict.values():
        pairlist.sort(key=lambda x: id(x[0]))
        pairlist.sort(key=lambda x: getattr(x[1], "_name", ""))
        varpairlists.append(pairlist)

    varassignpairs = list()
    for vp in itertools.zip_longest(*varpairlists):
        for varassignpair in vp:
            if varassignpair is not None:
                varassignpairs.append(varassignpair)

    SeqCompute(constpairs + varassignpairs)


def SetVariables(srclist, dstlist, mdtlist=None) -> None:  # noqa: N802
    if sys.version_info >= (3, 11):
        srclist_refcount = 2
        refcount = 3
    else:
        srclist_refcount = 3
        refcount = 4
    errlist = []
    if sys.getrefcount(srclist) == srclist_refcount:
        nth = 0
        for src, is_rvalue in _yield_and_check_rvalue(srclist, refcount):
            if isinstance(src, EUDVariable) and is_rvalue:
                errlist.append(EPError(_("src{} is RValue variable").format(nth)))
            nth += 1
    srclist = FlattenList(srclist)
    dstlist = FlattenList(dstlist)
    if len(srclist) != len(dstlist):
        errlist.append(EPError(_("Input/output size mismatch")))
    if len(errlist) == 1:
        raise errlist[0]
    elif errlist:
        if sys.version_info >= (3, 11):
            raise ExceptionGroup(
                _("Multiple error occurred on SetVariables:"), errlist
            )
        else:
            raise EPError(_("Multiple error occurred on SetVariables:"), errlist)

    if mdtlist is None:
        mdtlist = [bt.SetTo] * len(srclist)
    else:
        mdtlist = FlattenList(mdtlist)

    sqa = [(src, mdt, dst) for src, dst, mdt in zip(srclist, dstlist, mdtlist)]
    SeqCompute(sqa)
