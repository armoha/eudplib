#!/usr/bin/python
# -*- coding: utf-8 -*-

from .. import core as c


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer

    20 bytes per nextptr.
    """

    def __init__(self):
        super().__init__()

        self._jdict = {}
        self._nextptrs = []

    def DynamicConstructed(self):
        return True

    def CreateJumpTrigger(self, v, nextptr):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def CreateMultipleJumpTriggers(self, v, nextptrs):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2356 + 20 * len(self._nextptrs)

    def CollectDependency(self, emitbuffer):
        for nextptr in self._nextptrs:
            if type(nextptr) is not int:
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer):
        for nextptr in self._nextptrs[:17]:
            emitbuffer.WriteDword(nextptr)  # nextptr
            emitbuffer.WriteSpace(12)
            emitbuffer.WriteDword(0)  # nocond
        for nextptr in self._nextptrs[17:118]:
            emitbuffer.WriteDword(nextptr)  # nextptr
            emitbuffer.WriteSpace(4)
            emitbuffer.WriteDword(0)  # noact
            emitbuffer.WriteSpace(4)
            emitbuffer.WriteDword(0)  # nocond
        for nextptr in self._nextptrs[118:]:
            emitbuffer.WriteDword(nextptr)  # nextptr
            emitbuffer.WriteSpace(4)
            emitbuffer.WriteDword(0)  # noact
            emitbuffer.WriteDword(0)  # flags
            emitbuffer.WriteDword(0)  # nocond
        emitbuffer.WriteSpace(8)
        emitbuffer.WriteDword(0)  # noact
        emitbuffer.WriteDword(0)  # flags
        for _ in range(16):
            emitbuffer.WriteSpace(12)
            emitbuffer.WriteDword(0)  # noact
            emitbuffer.WriteDword(0)  # flags
        for _ in range(117 - 16):
            emitbuffer.WriteSpace(16)
            emitbuffer.WriteDword(0)  # flags


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
