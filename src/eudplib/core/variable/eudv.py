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
from typing import TYPE_CHECKING, Any, TypeGuard

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
from .vbuf import get_current_varbuffer

if TYPE_CHECKING:
    from ..rawtrigger.constenc import Dword, TrgModifier


_is_rvalue_strict = False


def EP_SetRValueStrictMode(mode: bool) -> None:  # noqa: N802
    global _is_rvalue_strict
    _is_rvalue_strict = mode


def process_dest(dest) -> int | ConstExpr:
    epd = unProxy(dest)
    if isinstance(epd, VariableBase):
        if isinstance(epd, EUDVariable):
            epd.checkNonRValue()
        return EPD(epd.getValueAddr())
    if not isinstance(epd, int | ConstExpr):
        raise EPError(_("Invalid dest: {}").format(dest))
    return epd


if sys.version_info >= (3, 11):
    _initial_refcount = 2
else:
    _initial_refcount = 3


def _is_rvalue(obj: object, refcount_bonus: int = 0, /) -> bool:
    refcount = _initial_refcount + 2 + refcount_bonus
    if isinstance(obj, EUDVariable) and sys.getrefcount(obj) != refcount:
        return False
    if isinstance(obj, ExprProxy) and not _is_rvalue(
        obj.getValue(), refcount_bonus + 1
    ):
        return False
    return True


def _yield_and_check_rvalue(
    obj: Any, refcount_bonus: int = 0, is_rvalue: bool = True
) -> Iterator[tuple[Any, bool]]:
    refcount = _initial_refcount + refcount_bonus
    is_rvalue &= sys.getrefcount(obj) <= refcount
    if isinstance(obj, ExprProxy):
        yield from _yield_and_check_rvalue(obj.getValue(), 1, is_rvalue)
    elif isinstance(obj, EUDVariable):
        yield obj, is_rvalue
    elif isinstance(obj, (bytes, str)) or hasattr(obj, "dont_flatten"):  # noqa: UP038
        yield obj, False
    else:
        try:
            for subobj in obj:
                yield from _yield_and_check_rvalue(subobj, 2, is_rvalue)
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

    def __init__(self, initval=0) -> None:
        if not isinstance(initval, (int, ConstExpr)):  # noqa: UP038
            unproxied = unProxy(initval)
            if not isinstance(unproxied, (int, ConstExpr)):  # noqa: UP038
                raise EPError(_("Invalid initval: {}").format(initval))
            else:
                initval = unproxied
        self._vartrigger = VariableTriggerForward(initval)
        self._varact = self._vartrigger + (8 + 320)
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
    def makeL(self) -> Self:  # noqa: N802
        self._rvalue = False
        return self

    def makeR(self) -> Self:  # noqa: N802
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

    def SetModifier(self, modifier: TrgModifier) -> bt.Action:  # noqa: N802
        ep_assert(
            modifier is bt.SetTo or modifier is bt.Add or modifier is bt.Subtract,
            _("Unexpected modifier {}").format(modifier),
        )
        mode = bt.EncodeModifier(modifier) << 24
        return bt.SetDeathsX(EPD(self._varact + 24), bt.SetTo, mode, 0, 0xFF000000)

    # -------

    def QueueAssignTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.SetTo)]

    def QueueAddTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.Add)]

    def QueueSubtractTo(self, dest) -> list[bt.Action]:  # noqa: N802
        return [self.SetDest(dest), self.SetModifier(bt.Subtract)]

    # -------

    def Assign(self, other: Dword) -> Self:  # noqa: N802
        self.checkNonRValue()
        SeqCompute(((self, bt.SetTo, other),))
        return self

    def __lshift__(self, other: Dword) -> Self:
        return self.Assign(other)

    def __iadd__(self, other: Dword) -> Self:
        SeqCompute(((self, bt.Add, other),))
        return self

    def __isub__(self, other: Dword) -> Self:
        if isinstance(other, int):
            self.__iadd__(-other)  # 1A
        else:
            from .evcommon import _addor as addor

            SeqCompute(
                [  # (self + 1) + (~0 - other)
                    (self, bt.Add, 1),
                    (addor, bt.SetTo, 0xFFFFFFFF),
                    (addor, bt.Subtract, other),
                    (self, None, addor),
                ]
            )  # 1T 7A, executes 3T 9A
        return self

    # -------

    def __add__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iadd__(other)
        is_rvalue = _is_rvalue(other)
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable) and is_rvalue:
            return unproxied.__iadd__(self)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, unproxied), (t, bt.Add, self)])
        return t.makeR()

    def __radd__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iadd__(other)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, other), (t, bt.Add, self)])
        return t.makeR()

    def __sub__(self, other: Dword) -> EUDVariable:
        is_rvalue = _is_rvalue(other)
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable) and is_rvalue:
            rvalue_strict = _is_rvalue_strict
            if rvalue_strict:
                EP_SetRValueStrictMode(False)
            VProc(
                self,  # -other += self
                [
                    unproxied.AddNumberX(0xFFFFFFFF, 0x55555555),
                    unproxied.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    unproxied.AddNumber(1),
                    self.QueueAddTo(unproxied),
                ],
            )  # 1T 7A, executes 2T 8A
            if rvalue_strict:
                EP_SetRValueStrictMode(True)
            return unproxied
        if _is_rvalue(self):
            return self.__isub__(unproxied)
        t = EUDVariable()
        # FIXME: unsupported EUD error after EUDStruct.free() with IsConstExpr
        if isinstance(unproxied, int):
            SeqCompute(
                [
                    (t, bt.SetTo, -unproxied),
                    (t, bt.Add, self),
                ]
            )
        else:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, unproxied),
                    (t, bt.Add, 1),
                    (t, bt.Add, self),
                ]
            )
        return t.makeR()

    def __rsub__(self, other: Dword) -> EUDVariable:
        unproxied = unProxy(other)
        is_eudvariable = isinstance(unproxied, EUDVariable)
        if _is_rvalue(self) and not is_eudvariable:
            bt.RawTrigger(  # -self += other
                actions=[
                    self.AddNumberX(0xFFFFFFFF, 0x55555555),
                    self.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    self.AddNumber(unproxied + 1),
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
                    (t, bt.Add, unproxied),
                ]
            )
        else:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, self),
                    (t, bt.Add, unproxied + 1),
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

    def __ior__(self, other: Dword) -> Self:
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable):
            write = self.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(EPD(write), bt.SetTo, unproxied)])
            bt.RawTrigger(actions=write)  # 1T 5A
        else:
            super().__ior__(unproxied)  # 1A
        return self

    def __iand__(self, other: Dword) -> Self:
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable):
            write = self.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (EPD(write), bt.Subtract, unproxied),
                ]
            )
            bt.RawTrigger(actions=write)  # 1T 6A
        else:
            super().__iand__(unproxied)  # 1A
        return self

    # -------

    def __and__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iand__(other)
        is_rvalue = _is_rvalue(other)
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable) and is_rvalue:
            return unproxied.__iand__(self)
        t = EUDVariable()
        if isinstance(unproxied, EUDVariable):
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, unproxied),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        else:
            t << self
            t &= unproxied  # 1T 5A
        return t.makeR()

    def __rand__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__iand__(other)
        t = EUDVariable()
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable):
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, unproxied),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        else:
            t << self
            t &= unproxied  # 1T 5A
        return t.makeR()

    def __or__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ior__(other)
        is_rvalue = _is_rvalue(other)
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable) and is_rvalue:
            return unproxied.__ior__(self)
        t = EUDVariable()
        if isinstance(unproxied, EUDVariable):
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, unproxied)])
            bt.RawTrigger(actions=write)  # 2T 9A
        else:
            t << self
            t |= unproxied  # 1T 5A
        return t.makeR()

    def __ror__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ior__(other)
        t = EUDVariable()
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable):
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, unproxied)])
            bt.RawTrigger(actions=write)  # 2T 9A
        else:
            t << self
            t |= unproxied  # 1T 5A
        return t.makeR()

    # -------

    def __ixor__(self, other: Dword) -> Self:
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable):
            VProc(
                unproxied,
                [
                    unproxied.SetMask(0x55555555),
                    *unproxied.QueueAddTo(self),
                ],
            )
            VProc(unproxied, unproxied.SetMask(0xAAAAAAAA))  # 3T 8A
            bt.RawTrigger(
                actions=unproxied.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            super().__ixor__(unproxied)  # 2A
        return self

    def __xor__(self, other: Dword) -> EUDVariable:
        if _is_rvalue(self):
            return self.__ixor__(other)
        is_rvalue = _is_rvalue(other)
        unproxied = unProxy(other)
        if isinstance(unproxied, EUDVariable) and is_rvalue:
            return unproxied.__ixor__(self)
        t = EUDVariable()
        if isinstance(unproxied, EUDVariable):
            VProc(
                [self, unproxied],
                [
                    unproxied.SetMask(0x55555555),
                    self.QueueAssignTo(t),
                    unproxied.QueueAddTo(t),
                ],
            )
            VProc(unproxied, unproxied.SetMask(0xAAAAAAAA))
            bt.RawTrigger(
                actions=unproxied.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            t << self
            t ^= unproxied
        return t.makeR()

    def __rxor__(self, other: Dword) -> EUDVariable:
        unproxied = unProxy(other)
        if _is_rvalue(self):
            return self.__ixor__(unproxied)
        t = EUDVariable()
        if isinstance(unproxied, EUDVariable):
            SeqCompute(
                [
                    (EPD(unproxied.getMaskAddr()), bt.SetTo, 0x55555555),
                    (t, bt.SetTo, self),
                    (t, bt.Add, unproxied),
                ]
            )
            VProc(unproxied, unproxied.SetMask(0xAAAAAAAA))
            bt.RawTrigger(
                actions=unproxied.SetMask(0xFFFFFFFF)
            )  # FIXME: restore to previous mask???
        else:
            t << self
            t ^= unproxied
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


def VProc(  # noqa: N802
    v: EUDVariable | Sequence[EUDVariable], actions
) -> bt.RawTrigger:
    v = FlattenList(v)
    actions = FlattenList(actions)
    end = Forward()
    first_trigger = None

    for cv, nv in pairwise(v):
        actions.append(bt.SetNextPtr(cv.GetVTable(), nv.GetVTable()))
    actions.append(bt.SetNextPtr(v[-1].GetVTable(), end))

    for i in range(0, len(actions), 64):
        trigger = bt.RawTrigger(actions=actions[i : i + 64])
        if first_trigger is None:
            first_trigger = trigger
    bt.SetNextTrigger(v[0].GetVTable())
    end << bt.NextTrigger()

    return first_trigger  # type: ignore[return-value]


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
    srclist_refcount = _initial_refcount
    errlist = []
    if sys.getrefcount(srclist) == srclist_refcount:
        nth = 0
        for src, is_rvalue in _yield_and_check_rvalue(srclist, 1):
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
