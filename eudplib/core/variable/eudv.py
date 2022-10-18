#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import traceback
from sys import getrefcount

from ...localize import _
from ...utils import (
    EPD,
    EPError,
    FlattenList,
    List2Assignable,
    RandList,
    ep_assert,
    ep_warn,
    isUnproxyInstance,
    unProxy,
)
from .. import rawtrigger as bt
from ..allocator import ConstExpr, Forward, IsConstExpr
from .vbase import VariableBase
from .vbuf import GetCurrentCustomVariableBuffer, GetCurrentVariableBuffer

isRValueStrict = False


def EP_SetRValueStrictMode(mode):
    global isRValueStrict
    isRValueStrict = mode


def _ProcessDest(dest):
    try:
        dest.checkNonRValue()
        dest = EPD(dest.getValueAddr())
    except AttributeError:
        if isinstance(dest, ConstExpr) and dest.rlocmode == 4:
            dest = ConstExpr(dest.baseobj, dest.offset // 4, 1)
        else:
            dest = bt.EncodePlayer(dest)
    return dest


def IsRValue(obj):
    # FIXME: Can we handle wrapped (ExprProxy) variables?
    return getrefcount(unProxy(obj)) == 3


# Unused variable don't need to be allocated.
class VariableTriggerForward(ConstExpr):
    def __init__(self, initval):
        super().__init__(self)
        self._initval = initval

    def Evaluate(self):
        if isinstance(self._initval, tuple):
            evb = GetCurrentCustomVariableBuffer()
        else:
            evb = GetCurrentVariableBuffer()
        try:
            return evb._vdict[self].Evaluate()
        except KeyError:
            vt = evb.CreateVarTrigger(self, self._initval)
            return vt.Evaluate()


class EUDVariable(VariableBase):

    """
    Full variable.
    """

    def __init__(self, _initval=0, modifier=None, /, initval=None, *, nextptr=None):
        if not (modifier is None and initval is None and nextptr is None):
            if modifier is None:
                modifier = 0x072D0000
            else:
                modifier = ((bt.EncodeModifier(modifier) & 0xFF) << 24) | 0x2D0000
            if initval is None:
                initval = 0
            if nextptr is None:
                nextptr = 0
            # bitmask, player, #, modifier, nextptr
            _initval = (0xFFFFFFFF, _ProcessDest(_initval), initval, modifier, nextptr)
        self._vartrigger = VariableTriggerForward(_initval)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False

    def GetVTable(self):
        return self._vartrigger

    def getMaskAddr(self):
        return self._varact

    def getDestAddr(self):
        return self._varact + 16

    def getValueAddr(self):
        return self._varact + 20

    def __hash__(self):
        return id(self)

    # -------
    def makeL(self):
        self._rvalue = False
        return self

    def makeR(self):
        self._rvalue = True
        return self

    def checkNonRValue(self):
        if isRValueStrict and self._rvalue:
            raise EPError(_("Trying to modify value of l-value variable"))

    # -------

    def SetMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.SetTo, value)

    def AddMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.Add, value)

    def SubtractMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.Subtract, value)

    # -------

    def SetMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.SetTo, value, mask)

    def AddMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.Add, value, mask)

    def SubtractMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.Subtract, value, mask)

    # -------

    def MaskAtLeast(self, value):
        return bt.Memory(self.getMaskAddr(), bt.AtLeast, value)

    def MaskAtMost(self, value):
        return bt.Memory(self.getMaskAddr(), bt.AtMost, value)

    def MaskExactly(self, value):
        return bt.Memory(self.getMaskAddr(), bt.Exactly, value)

    # -------

    def MaskAtLeastX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.AtLeast, value, mask)

    def MaskAtMostX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.AtMost, value, mask)

    def MaskExactlyX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.Exactly, value, mask)

    # -------

    def SetDest(self, dest):
        dest = _ProcessDest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.SetTo, dest)

    def AddDest(self, dest):
        dest = _ProcessDest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.Add, dest)

    def SubtractDest(self, dest):
        dest = _ProcessDest(dest)
        return bt.SetMemory(self.getDestAddr(), bt.Subtract, dest)

    # -------

    def SetDestX(self, dest, mask):
        dest = _ProcessDest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.SetTo, dest, mask)

    def AddDestX(self, dest, mask):
        dest = _ProcessDest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.Add, dest, mask)

    def SubtractDestX(self, dest, mask):
        dest = _ProcessDest(dest)
        return bt.SetMemoryX(self.getDestAddr(), bt.Subtract, dest, mask)

    # -------

    def SetModifier(self, modifier):
        ep_assert(
            modifier in (bt.SetTo, bt.Add, bt.Subtract),
            "Unexpected modifier {}".format(modifier),
        )
        modifier = bt.EncodeModifier(modifier) << 24
        return (
            bt.SetDeathsX(EPD(self._varact + 24), bt.SetTo, modifier, 0, 0xFF000000),
        )

    # -------

    def QueueAssignTo(self, dest):
        return [self.SetDest(dest), self.SetModifier(bt.SetTo)]

    def QueueAddTo(self, dest):
        return [self.SetDest(dest), self.SetModifier(bt.Add)]

    def QueueSubtractTo(self, dest):
        return [self.SetDest(dest), self.SetModifier(bt.Subtract)]

    # -------

    def Assign(self, other):
        self.checkNonRValue()
        SeqCompute(((self, bt.SetTo, other),))

    def __lshift__(self, other):
        self.Assign(other)
        return self

    def __iadd__(self, other):
        SeqCompute(((self, bt.Add, other),))
        return self

    def __isub__(self, other):
        if isinstance(other, int):
            return self.__iadd__(-other)  # 1A
        try:
            addor = EUDVariable.addor
        except AttributeError:
            addor = EUDVariable(0, bt.Add, 0)
            EUDVariable.addor = addor
        SeqCompute(
            [  # (~0 - other) + (self + 1)
                (self, bt.Add, 1),
                (addor, bt.SetTo, 0xFFFFFFFF),
                (addor, bt.Subtract, other),
                (self, None, addor),
            ]
        )
        return self

    # -------

    def __add__(self, other):
        if IsRValue(self):
            return self.__iadd__(other)
        if IsEUDVariable(other) and IsRValue(other):
            return other.__iadd__(self)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, other), (t, bt.Add, self)])
        return t.makeR()

    def __radd__(self, other):
        if IsRValue(self):
            return self.__iadd__(other)
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, other), (t, bt.Add, self)])
        return t.makeR()

    def __sub__(self, other):
        if IsEUDVariable(other) and IsRValue(other):
            VProc(
                self,  # -other += self
                [
                    other.AddNumberX(0xFFFFFFFF, 0x55555555),
                    other.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    other.AddNumber(1),
                    self.QueueAddTo(other),
                ],
            )  # 1T 7A
            return other
        if IsRValue(self):
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

    def __rsub__(self, other):
        if IsRValue(self) and IsConstExpr(other):
            bt.RawTrigger(  # -self += other
                actions=[
                    self.AddNumberX(0xFFFFFFFF, 0x55555555),
                    self.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                    self.AddNumber(other + 1),
                ]
            )
            return self
        t = EUDVariable()
        if IsConstExpr(other):
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, self),
                    (t, bt.Add, other + 1),
                ]
            )
        else:
            SeqCompute(
                [
                    (t, bt.SetTo, 0xFFFFFFFF),
                    (t, bt.Subtract, self),
                    (t, bt.Add, 1),
                    (t, bt.Add, other),
                ]
            )
        return t.makeR()

    def __neg__(self):
        if IsRValue(self):
            return self.ineg()
        return (0 - self).makeR()

    def __invert__(self):
        if IsRValue(self):
            return self.iinvert()
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, 0xFFFFFFFF), (t, bt.Subtract, self)])
        return t.makeR()

    # -------

    def __ior__(self, other):
        if IsConstExpr(other):
            return super().__ior__(other)  # 1A
        write = self.SetNumberX(0xFFFFFFFF, 0)
        SeqCompute([(EPD(write), bt.SetTo, other)])
        bt.RawTrigger(actions=write)  # 1T 5A
        return self

    def __iand__(self, other):
        if IsConstExpr(other):
            return super().__iand__(other)  # 1A
        write = self.SetNumberX(0, 0xFFFFFFFF)
        SeqCompute(
            [(EPD(write), bt.SetTo, 0xFFFFFFFF), (EPD(write), bt.Subtract, other)]
        )
        bt.RawTrigger(actions=write)  # 1T 6A
        return self

    # -------

    def __and__(self, other):
        if IsRValue(self):
            return self.__iand__(other)
        if IsEUDVariable(other) and IsRValue(other):
            return other.__iand__(self)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t &= other  # 1T 5A
        else:
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, other),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        return t.makeR()

    def __rand__(self, other):
        if IsRValue(self):
            return self.__iand__(other)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t &= other  # 1T 5A
        else:
            write = t.SetNumberX(0, 0xFFFFFFFF)
            SeqCompute(
                [
                    (EPD(write), bt.SetTo, 0xFFFFFFFF),
                    (t, bt.SetTo, self),
                    (EPD(write), bt.Subtract, other),
                ]
            )
            bt.RawTrigger(actions=write)  # 2T 10A
        return t.makeR()

    def __or__(self, other):
        if IsRValue(self):
            return self.__ior__(other)
        if IsEUDVariable(other) and IsRValue(other):
            return other.__ior__(self)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t |= other  # 1T 5A
        else:
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, other)])
            bt.RawTrigger(actions=write)  # 2T 9A
        return t.makeR()

    def __ror__(self, other):
        if IsRValue(self):
            return self.__ior__(other)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t |= other  # 1T 5A
        else:
            write = t.SetNumberX(0xFFFFFFFF, 0)
            SeqCompute([(t, bt.SetTo, self), (EPD(write), bt.SetTo, other)])
            bt.RawTrigger(actions=write)  # 2T 9A
        return t.makeR()

    # -------

    def __ixor__(self, other):
        if IsConstExpr(other):
            return super().__ixor__(other)  # 2A
        else:
            VProc(
                other,
                [
                    other.SetMask(0x55555555),
                    other.QueueAddTo(self),
                ],
            )
            VProc(other, other.SetMask(0xAAAAAAAA))  # 3T 8A
            bt.RawTrigger(  # FIXME: restore to previous mask???
                actions=other.SetMask(0xFFFFFFFF)
            )
        return self

    def __xor__(self, other):
        if IsRValue(self):
            return self.__ixor__(other)
        if IsEUDVariable(other) and IsRValue(other):
            return other.__ixor__(self)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t ^= other
        else:
            VProc(
                [self, other],
                [
                    other.SetMask(0x55555555),
                    self.QueueAssignTo(t),
                    other.QueueAddTo(t),
                ],
            )
            VProc(other, other.SetMask(0xAAAAAAAA))
            bt.RawTrigger(  # FIXME: restore to previous mask???
                actions=other.SetMask(0xFFFFFFFF)
            )
        return t.makeR()

    def __rxor__(self, other):
        if IsRValue(self):
            return self.__ixor__(other)
        t = EUDVariable()
        if IsConstExpr(other):
            t << self
            t ^= other
        else:
            SeqCompute(
                [
                    (EPD(other.getMaskAddr()), bt.SetTo, 0x55555555),
                    (t, bt.SetTo, self),
                    (t, bt.Add, other),
                ]
            )
            VProc(other, other.SetMask(0xAAAAAAAA))
            bt.RawTrigger(  # FIXME: restore to previous mask???
                actions=other.SetMask(0xFFFFFFFF)
            )
        return t.makeR()

    # -------

    def __eq__(self, other):
        try:
            return self.Exactly(other)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            return (self - other).Exactly(0)

    def __ne__(self, other):
        if isinstance(other, int):
            if other & 0xFFFFFFFF == 0:
                return self.AtLeast(1)
            if other & 0xFFFFFFFF == 0xFFFFFFFF:
                return self.AtMost(0xFFFFFFFE)
        return (self - other).AtLeast(1)

    def __le__(self, other):
        try:
            return self.AtMost(other)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, self), (t, bt.Subtract, other)))
            return t.Exactly(0)

    def __ge__(self, other):
        try:
            return self.AtLeast(other)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, other), (t, bt.Subtract, self)))
            return t.Exactly(0)

    def __lt__(self, other):
        if isinstance(other, int) and other <= 0:
            ep_warn(_("No unsigned number can be leq than {}").format(other))
            traceback.print_stack()
            return [bt.Never()]  # No unsigned number is less than 0

        try:
            return self.AtMost(other - 1)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, 1), (t, bt.Add, self), (t, bt.Subtract, other)))
            return t.Exactly(0)

    def __gt__(self, other):
        if isinstance(other, int) and other >= 0xFFFFFFFF:
            ep_warn(_("No unsigned number can be greater than {}").format(other))
            traceback.print_stack()
            return [bt.Never()]  # No unsigned number is less than 0

        try:
            return self.AtLeast(other + 1)

        except Exception as err:
            ep_warn(_("{}: Comparing with temporary variable.").format(err))
            traceback.print_stack()
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, self), (t, bt.Subtract, other)))
            return t.AtLeast(1)

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

    def __ilshift__(self, a):
        raise NotImplementedError

    def __irshift__(self, a):
        raise NotImplementedError


def IsEUDVariable(x):
    return isUnproxyInstance(x, EUDVariable)


# ---------


def VProc(v, actions):
    v = FlattenList(v)
    actions = FlattenList(actions)
    end = Forward()
    triggers = list()

    for cv, nv in zip(v, v[1:]):
        actions.append(bt.SetNextPtr(cv.GetVTable(), nv.GetVTable()))
    actions.append(bt.SetNextPtr(v[-1].GetVTable(), end))

    for i in range(0, len(actions), 64):
        trg = bt.RawTrigger(actions=actions[i : i + 64])
        triggers.append(trg)
    triggers[-1]._nextptr = v[0].GetVTable()
    end << bt.NextTrigger()

    return List2Assignable(triggers)


# From vbuffer.py
def EUDCreateVariables(varn):
    return List2Assignable([EUDVariable() for _ in range(varn)])


# -------


def _GetComputeDest(dst):
    try:
        return EPD(dst.getValueAddr())
    except AttributeError:
        return dst


def _SeqComputeSub(assignpairs, _srcdict={}):
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
        dst = _GetComputeDest(dst)
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
    nonConstActions = list()

    def _RemoveDuplicateActions():
        if last_pairs is None:
            return
        last_src, last_dst, last_mdt = last_pairs
        try:
            prev_dst, prev_mdt, prev_nptr = _srcdict[last_src]
        except KeyError:
            pass
        else:
            lastact = nonConstActions[-1]
            queueact, setnptr = lastact
            setdst, setmdt = queueact
            if last_dst is prev_dst:
                queueact.remove(setdst)
            if last_mdt is prev_mdt:
                queueact.remove(setmdt)
            if vt_nextptr._expr is prev_nptr._expr:
                lastact.remove(setnptr)
        _srcdict[last_src] = (last_dst, last_mdt, vt_nextptr)

    for dst, mdt, src in assignpairs[const_assigning_index:]:
        dst = _GetComputeDest(dst)

        if nextptr is None:
            nextptr = src.GetVTable()
        else:
            vt_nextptr << src.GetVTable()

        _RemoveDuplicateActions()

        vt_nextptr = Forward()
        nonConstAction = []
        if dst is None:
            nonConstAction.append([])
        else:
            nonConstAction.append(src.SetDest(dst))
        if mdt is None:
            nonConstAction.append([])
        else:
            nonConstAction.append(src.SetModifier(mdt))

        nonConstActions.append(
            [nonConstAction, bt.SetNextPtr(src.GetVTable(), vt_nextptr)]
        )
        last_pairs = src, dst, mdt

    _RemoveDuplicateActions()
    bt.RawTrigger(nextptr=nextptr, actions=[actionlist, RandList(nonConstActions)])

    vt_nextptr << bt.NextTrigger()


def SeqCompute(assignpairs):
    # We need dependency map while writing assignment pairs
    dstvarset = set()
    srcvarset = set()

    # Record previous dst, mdt for src to optimize duplicate actions
    import inspect

    srcdictsub = inspect.signature(_SeqComputeSub).parameters["_srcdict"].default
    srcdict = {}

    # Sublist of assignments to put in _SeqComputeSub
    subassignpairs = []

    # Is we collecting constant-assigning pairs?
    constcollecting = True

    # Number of expected actions.
    actioncount = 0

    def FlushPairs():
        nonlocal constcollecting, actioncount

        if actioncount == 0:  # Already flushed before
            return

        _SeqComputeSub(subassignpairs)

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
            if src in dstvarset:
                FlushPairs()
            elif src in srcvarset:
                FlushPairs()
            elif actioncount >= 64 - 3:
                FlushPairs()

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
                FlushPairs()
            elif actioncount >= 64 - 3:
                FlushPairs()

            actioncount += 1

        subassignpairs.append((dst, mdt, src))
        if IsEUDVariable(dst):
            dstvarset.add(dst)

    FlushPairs()
    srcdictsub.clear()


def NonSeqCompute(assignpairs):
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
        pairlist.sort(key=lambda x: x[1]._name)
        varpairlists.append(pairlist)

    varassignpairs = list()
    for vp in itertools.zip_longest(*varpairlists):
        for varassignpair in vp:
            if varassignpair is not None:
                varassignpairs.append(varassignpair)

    SeqCompute(constpairs + varassignpairs)


def SetVariables(srclist, dstlist, mdtlist=None):
    srclist = FlattenList(srclist)
    dstlist = FlattenList(dstlist)
    ep_assert(len(srclist) == len(dstlist), _("Input/output size mismatch"))

    if mdtlist is None:
        mdtlist = [bt.SetTo] * len(srclist)
    else:
        mdtlist = FlattenList(mdtlist)

    sqa = [(src, mdt, dst) for src, dst, mdt in zip(srclist, dstlist, mdtlist)]
    SeqCompute(sqa)
