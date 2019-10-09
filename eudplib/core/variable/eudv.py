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

from .. import rawtrigger as bt
from ..allocator import Forward, ConstExpr, IsConstExpr
from ...utils import (
    FlattenList,
    EPD,
    List2Assignable,
    unProxy,
    isUnproxyInstance,
    ep_assert,
    EPError,
)
from .vbase import VariableBase
from .vbuf import GetCurrentVariableBuffer


isRValueStrict = False


def EP_SetRValueStrictMode(mode):
    global isRValueStrict
    isRValueStrict = mode


def _ProcessDest(dest):
    try:
        dest.checkNonRValue()
        dest = EPD(dest.getValueAddr())
    except AttributeError:
        pass
    return dest


# Unused variable don't need to be allocated.
class VariableTriggerForward(ConstExpr):
    def __init__(self, initval, mask=None):
        super().__init__(self)
        self._initval = initval
        self._mask = mask

    def Evaluate(self):
        evb = GetCurrentVariableBuffer()
        try:
            return evb._vdict[self].Evaluate()
        except KeyError:
            vt = evb.CreateVarTrigger(self, self._initval, self._mask)
            return vt.Evaluate()


class EUDVariable(VariableBase):

    """
    Full variable.
    """

    def __init__(self, initval=0):
        self._vartrigger = VariableTriggerForward(initval)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False

    def GetVTable(self):
        return self._vartrigger

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
            raise EPError("Trying to modify value of l-value variable")

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

    def QueueAssignTo(self, dest):
        return [
            self.SetDest(dest),
            bt.SetDeaths(EPD(self._varact + 24), bt.SetTo, 0x072D0000, 0),
        ]

    def QueueAddTo(self, dest):
        return [
            self.SetDest(dest),
            bt.SetDeaths(EPD(self._varact + 24), bt.SetTo, 0x082D0000, 0),
        ]

    def QueueSubtractTo(self, dest):
        return [
            self.SetDest(dest),
            bt.SetDeaths(EPD(self._varact + 24), bt.SetTo, 0x092D0000, 0),
        ]

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
        self << self - other
        return self

    # -------

    def __add__(self, other):
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, self), (t, bt.Add, other)])
        return t.makeR()

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        t = EUDVariable()

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
        t = EUDVariable()
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
        return (0 - self).makeR()

    def __invert__(self):
        t = EUDVariable()
        SeqCompute([(t, bt.SetTo, 0xFFFFFFFF), (t, bt.Subtract, self)])
        return t.makeR()

    # -------

    def __eq__(self, other):
        if IsConstExpr(other):
            return self.Exactly(other)

        else:
            return (self - other).Exactly(0)

    def __ne__(self, other):
        if isinstance(other, int) and other == 0:
            return self.AtLeast(1)
        else:
            return (self - other).AtLeast(1)

    def __le__(self, other):
        if IsConstExpr(other):
            return self.AtMost(other)

        else:
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, self), (t, bt.Subtract, other)))
            return t.Exactly(0)

    def __ge__(self, other):
        if IsConstExpr(other):
            return self.AtLeast(other)

        else:
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, other), (t, bt.Subtract, self)))
            return t.Exactly(0)

    def __lt__(self, other):
        if isinstance(other, int) and other <= 0:
            print("[Warning] No unsigned number can be leq than %d" % other)
            traceback.print_stack()
            return [bt.Never()]  # No unsigned number is less than 0

        if IsConstExpr(other):
            return self.AtMost(other - 1)

        else:
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, 1), (t, bt.Add, self), (t, bt.Subtract, other)))
            return t.Exactly(0)

    def __gt__(self, other):
        if isinstance(other, int) and other >= 0xFFFFFFFF:
            print("[Warning] No unsigned int can be greater than %d" % other)
            traceback.print_stack()
            return [bt.Never()]  # No unsigned number is less than 0

        if IsConstExpr(other):
            return self.AtLeast(other + 1)

        else:
            t = EUDVariable()
            SeqCompute(((t, bt.SetTo, self), (t, bt.Subtract, other)))
            return t.AtLeast(1)

    # operator placeholders
    def __mul__(self, a):
        pass

    def __rmul__(self, a):
        pass

    def __imul__(self, a):
        pass

    def __floordiv__(self, a):
        raise NotImplementedError("")

    def __rfloordiv__(self, a):
        pass

    def __ifloordiv__(self, a):
        pass

    def __mod__(self, a):
        pass

    def __rmod__(self, a):
        pass

    def __imod__(self, a):
        pass

    def __and__(self, a):
        pass

    def __rand__(self, a):
        pass

    def __iand__(self, a):
        pass

    def __or__(self, a):
        pass

    def __ror__(self, a):
        pass

    def __ior__(self, a):
        pass

    def __xor__(self, a):
        pass

    def __rxor__(self, a):
        pass

    def __ixor__(self, a):
        pass


def IsEUDVariable(x):
    return isUnproxyInstance(x, EUDVariable)


# ---------


def VProc(v, actions):
    nexttrg = Forward()

    try:
        v = FlattenList(v)
        trg = bt.RawTrigger(
            nextptr=v[0].GetVTable(),
            actions=[actions] + [bt.SetNextPtr(v[i].GetVTable(), v[i+1].GetVTable()) for i in range(len(v)-1)] + [bt.SetNextPtr(v[-1].GetVTable(), nexttrg)]
        )
    except (TypeError):
        trg = bt.RawTrigger(
            nextptr=v.GetVTable(),
            actions=[actions] + [bt.SetNextPtr(v.GetVTable(), nexttrg)],
        )

    nexttrg << bt.NextTrigger()
    return trg


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

    def _RemoveDuplicateActions():
        if last_pairs is None:
            return
        last_src, last_dst, last_mdt = last_pairs
        try:
            prev_dst, prev_mdt, prev_nptr = _srcdict[last_src]
        except KeyError:
            pass
        else:
            lastact = actionlist[-1]
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
        queuef = {
            bt.SetTo: EUDVariable.QueueAssignTo,
            bt.Add: EUDVariable.QueueAddTo,
            bt.Subtract: EUDVariable.QueueSubtractTo,
        }[mdt]

        actionlist.append(
            [queuef(src, dst), bt.SetNextPtr(src.GetVTable(), vt_nextptr)]
        )
        last_pairs = src, dst, mdt

    bt.RawTrigger(nextptr=nextptr, actions=actionlist)

    vt_nextptr << bt.NextTrigger()
    _RemoveDuplicateActions()


def SeqCompute(assignpairs):
    # We need dependency map while writing assignment pairs
    dstvarset = set()
    srcvarset = set()

    # Record previous dst, mdt for src to optimize duplicate actions
    import inspect
    srcdictsub = inspect.signature(_SeqComputeSub).parameters['_srcdict'].default
    srcdict={}

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

        # Flush action set before preceeding
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
            if actioncount >= 64 - 3:
                FlushPairs()
            elif isinstance(src, int):
                pass
            elif not constcollecting:
                FlushPairs()

            actioncount += 1

        subassignpairs.append((dst, mdt, src))
        if IsEUDVariable(dst):
            dstvarset.add(dst)

    FlushPairs()
    srcdictsub.clear()


def SetVariables(srclist, dstlist, mdtlist=None):
    srclist = FlattenList(srclist)
    dstlist = FlattenList(dstlist)
    ep_assert(len(srclist) == len(dstlist), "Input/output size mismatch")

    if mdtlist is None:
        mdtlist = [bt.SetTo] * len(srclist)

    sqa = [(src, mdt, dst) for src, dst, mdt in zip(srclist, dstlist, mdtlist)]
    SeqCompute(sqa)
