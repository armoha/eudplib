#!/usr/bin/python

from .. import core as c


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer

    20 bytes per nextptr.
    """

    def __init__(self):
        super().__init__()

        self._jdict = {}
        self._nextptrs = []

    def DynamicConstructed(self):  # noqa: N802
        return True

    def create_jump_trigger(self, v, nextptr):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def create_jump_triggers(self, v, nextptrs):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):  # noqa: N802
        return 2356 + 20 * len(self._nextptrs)

    def CollectDependency(self, emitbuffer):  # noqa: N802
        for nextptr in self._nextptrs:
            if not isinstance(nextptr, int):
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer):  # noqa: N802
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
            emitbuffer.WriteDword(8)  # flags
            emitbuffer.WriteDword(0)  # nocond
        emitbuffer.WriteSpace(8)
        emitbuffer.WriteDword(0)  # noact
        emitbuffer.WriteDword(8)  # flags
        for _ in range(16):
            emitbuffer.WriteSpace(12)
            emitbuffer.WriteDword(0)  # noact
            emitbuffer.WriteDword(8)  # flags
        for _ in range(117 - 16):
            emitbuffer.WriteSpace(16)
            emitbuffer.WriteDword(8)  # flags


_jtb = None


def register_new_jumpbuffer():
    global _jtb
    _jtb = EUDJumpBuffer()


def get_current_jumpbuffer():
    return _jtb


c.RegisterCreatePayloadCallback(register_new_jumpbuffer)


# Unused jump table don't need to be allocated.
class JumpTriggerForward(c.ConstExpr):
    def __init__(self, nextptrs):
        super().__init__(self)
        self._nextptrs = nextptrs

    def Evaluate(self):  # noqa: N802
        jtb = get_current_jumpbuffer()
        try:
            return jtb._jdict[self].Evaluate()
        except KeyError:
            jt = jtb.create_jump_triggers(self, self._nextptrs)
            return jt.Evaluate()
