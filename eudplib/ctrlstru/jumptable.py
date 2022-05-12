#!/usr/bin/python
# -*- coding: utf-8 -*-

from .. import core as c


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer

    12 bytes per nextptr.
    """

    def __init__(self):
        super().__init__()

        self._jdict = {}
        self._nextptrs = []

    def DynamicConstructed(self):
        return True

    def CreateJumpTrigger(self, v, nextptr):
        ret = self + (12 * len(self._nextptrs))
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def CreateMultipleJumpTriggers(self, v, nextptrs):
        ret = self + (12 * len(self._nextptrs))
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):
        return 344 + 12 * len(self._nextptrs)

    def CollectDependency(self, emitbuffer):
        for nextptr in self._nextptrs:
            if type(nextptr) is not int:
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteSpace(4)
        for nextptr in self._nextptrs:
            emitbuffer.WriteDword(nextptr)  # nextptr
            emitbuffer.WriteDword(0)  # nocond
            emitbuffer.WriteDword(0)  # noact
        emitbuffer.WriteSpace(4)
        emitbuffer.WriteDword(0)  # nocond
        emitbuffer.WriteSpace(4 + 15 * 20 + 24)  # 328
        emitbuffer.WriteDword(0)  # noact


_jtb = None


def RegisterNewJumpBuffer():
    global _jtb
    _jtb = EUDJumpBuffer()


def GetCurrentJumpBuffer():
    return _jtb


RegisterCreatePayloadCallback(RegisterNewJumpBuffer)


# Unused jump table don't need to be allocated.
class JumpTriggerForward(c.ConstExpr):
    def __init__(self, nextptr):
        super().__init__(self)
        self._nextptr = nextptr

    def Evaluate(self):
        jtb = GetCurrentJumpBuffer()
        try:
            return jtb._jdict[self].Evaluate()
        except KeyError:
            jt = evb.CreateJumpTrigger(self, self._nextptr)
            return jt.Evaluate()
