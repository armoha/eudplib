#!/usr/bin/python
# -*- coding: utf-8 -*-

from .. import core as c


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer

    8 bytes per nextptr.
    """

    def __init__(self):
        super().__init__()

        self._jdict = {}
        self._nextptrs = []

    def DynamicConstructed(self):
        return True

    def CreateJumpTrigger(self, v, nextptr):
        ret = self + (8 * len(self._nextptrs) - 4)
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def CreateMultipleJumpTriggers(self, v, nextptrs):
        ret = self + (8 * len(self._nextptrs) - 4)
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2376 + 8 * (len(self._nextptrs) - 1)

    def CollectDependency(self, emitbuffer):
        for nextptr in self._nextptrs:
            if type(nextptr) is not int:
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer):
        _space = 0

        def space(n):
            nonlocal _space
            _space += n

        def flush():
            nonlocal _space
            if _space:
                emitbuffer.WriteSpace(_space)
                _space = 0

        def byte(b):
            flush()
            emitbuffer.WriteByte(b)

        def dword(dw):
            flush()
            emitbuffer.WriteDword(dw)

        for i in range(296 + len(self._nextptrs)):
            if i < len(self._nextptrs):
                dword(self._nextptrs[i])
            else:
                space(4)
            if i < 296:
                space(4)
            else:
                byte(8)
                space(3)

        flush()


_jtb = None


def RegisterNewJumpBuffer():
    global _jtb
    _jtb = EUDJumpBuffer()


def GetCurrentJumpBuffer():
    return _jtb


c.RegisterCreatePayloadCallback(RegisterNewJumpBuffer)


# Unused jump table don't need to be allocated.
class JumpTriggerForward(c.ConstExpr):
    def __init__(self, nextptrs):
        super().__init__(self)
        self._nextptrs = nextptrs

    def Evaluate(self):
        jtb = GetCurrentJumpBuffer()
        try:
            return jtb._jdict[self].Evaluate()
        except KeyError:
            jt = jtb.CreateMultipleJumpTriggers(self, self._nextptrs)
            return jt.Evaluate()
