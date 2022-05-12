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
        self._initvals = []

    def DynamicConstructed(self):
        return True

    def CreateJumpTrigger(self, v, initval):
        ret = self + (12 * len(self._initvals))
        self._initvals.append(initval)
        self._jdict[v] = ret
        return ret

    def CreateMultipleJumpTriggers(self, v, initvals):
        ret = self + (12 * len(self._initvals))
        self._initvals.extend(initvals)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):
        return 344 + 12 * len(self._initvals)

    def CollectDependency(self, emitbuffer):
        for initval in self._initvals:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteSpace(4)
        for initval in self._initvals:
            emitbuffer.WriteDword(initval)  # nextptr
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
