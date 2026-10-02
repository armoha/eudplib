# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal

from typing_extensions import Self

from .. import core as c
from ..localize import _
from ..utils import ep_assert

# The engine reads a trigger node as [prev(4)][next(4)][TRIGGER(2400)] and a
# skipped (TF_COMPLETE) trigger only at its m_next (node + 4) and lFlags
# (node + 8 + 2368 = node + 2376). The jump buffer omits the unused prev
# field, so the object's byte 0 is the node's m_next and Evaluate() points to
# the node (object address - 4). Relative to each entry the nextptr sits at
# +0 and its lFlags at +2372, so entry k's lFlags is always exactly 2372
# bytes after its own nextptr.
_LFLAGS_OFFSET = 2372

# Stride 4: entry k's lFlags (4k + 2372 = 4(k + 593) + 0) lands exactly on
# another entry's nextptr, so S=4 buffers are limited to 593 entries.
# (2372 = 4 * 593.)
_STRIDE4_MAX = _LFLAGS_OFFSET // 4  # 593

# Stride 8: 2372 = 8 * 296 + 4, so entry k's lFlags lands on entry
# (k + 296)'s dead space at offset 4. No nextptr collision for any table
# size, so S=8 buffers are shared by all larger tables.
_STRIDE_LARGE = 8

# Effective capacity per buffer. S=8 has no geometric limit.
_STRIDE_MAX = {4: _STRIDE4_MAX, _STRIDE_LARGE: 0x7FFFFFFF}


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer.

    Array of jump triggers at a fixed stride. Every entry stores a single
    nextptr; the engine follows it as ``m_next`` (the node is the object
    address - 4) and never evaluates the body because the entry's ``lFlags``
    position (entry + 2372) is pre-set to ``TF_COMPLETE``.

    :param stride: Distance between consecutive entries, either 4 (max 593
        entries per buffer) or 8 (unbounded).
    """

    def __new__(cls, stride: int) -> Self:
        return super().__new__(cls)

    def __init__(self, stride: int) -> None:
        ep_assert(
            stride in _STRIDE_MAX,
            _(
                "Invalid jump buffer stride: {stride}. Only 4 or 8 is allowed."
            ).format(stride=stride),
        )
        super().__init__()

        self._stride = stride
        self._jdict: dict[JumpTriggerForward, c.ConstExpr] = {}
        self._nextptrs: list[int | c.ConstExpr] = []

    def DynamicConstructed(self) -> Literal[True]:  # noqa: N802
        return True

    def Evaluate(self) -> c.RlocInt_C:  # noqa: N802
        return c.GetObjectAddr(self) - 4

    def create_jump_trigger(self, v, nextptr) -> c.ConstExpr:
        ep_assert(
            self._stride != 4 or len(self._nextptrs) + 1 <= _STRIDE4_MAX,
            _("S=4 jump buffer can't hold more than {max} entries").format(
                max=_STRIDE4_MAX
            ),
        )
        ret = self + self._stride * len(self._nextptrs)
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def create_jump_triggers(self, v, nextptrs) -> c.ConstExpr:
        ep_assert(
            self._stride != 4 or len(self._nextptrs) + len(nextptrs) <= _STRIDE4_MAX,
            _("S=4 jump buffer can't hold more than {max} entries").format(
                max=_STRIDE4_MAX
            ),
        )
        ret = self + self._stride * len(self._nextptrs)
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self) -> int:  # noqa: N802
        return _LFLAGS_OFFSET + self._stride * len(self._nextptrs)

    def CollectDependency(self, emitbuffer) -> None:  # noqa: N802
        for nextptr in self._nextptrs:
            if not isinstance(nextptr, int):
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer) -> None:  # noqa: N802
        nextptr_count = len(self._nextptrs)
        if self._stride == 4:
            ep_assert(
                nextptr_count <= _STRIDE4_MAX,
                _("S=4 jump buffer can't hold more than {max} entries").format(
                    max=_STRIDE4_MAX
                ),
            )
            for nextptr in self._nextptrs:
                emitbuffer.WriteDword(nextptr)  # m_next at 4k+0
            emitbuffer.WriteSpace(_LFLAGS_OFFSET - 4 * nextptr_count)
            for _i in range(nextptr_count):
                emitbuffer.WriteDword(8)  # lFlags = TF_COMPLETE at 4k+2372
        else:
            stride = self._stride
            # entry k's lFlags at stride*k + 2372 lands on entry
            # (k + shift)'s dead space at offset rem (2372 = stride*shift+rem).
            shift = _LFLAGS_OFFSET // stride
            rem = _LFLAGS_OFFSET % stride
            for j, nextptr in enumerate(self._nextptrs):
                emitbuffer.WriteDword(nextptr)  # m_next at stride*k+0
                emitbuffer.WriteSpace(rem - 4)  # stride*k+4 .. rem-1
                if j >= shift:
                    # lFlags of entry (j - shift) at stride*j + rem
                    emitbuffer.WriteDword(8)
                else:
                    emitbuffer.WriteSpace(4)  # stride*k+rem .. rem+3
                emitbuffer.WriteSpace(stride - rem - 4)
            k0 = max(nextptr_count - shift, 0)
            first_flag = stride * k0 + _LFLAGS_OFFSET
            emitbuffer.WriteSpace(first_flag - stride * nextptr_count)
            for _i in range(nextptr_count - k0):
                emitbuffer.WriteDword(8)
                emitbuffer.WriteSpace(stride - 4)

        ep_assert(
            len(self._nextptrs) == nextptr_count,
            _("jump triggers were created while writing the jump buffer"),
        )


_jtb4: list[EUDJumpBuffer] = []
_jtb8: list[EUDJumpBuffer] = []


def _reset_jumpbuffers() -> None:
    global _jtb4, _jtb8
    _jtb4 = []
    _jtb8 = []


def _select_buffer(stride: int, entry_count: int) -> EUDJumpBuffer:
    buf_list = _jtb4 if stride == 4 else _jtb8
    for buf in buf_list:
        if _STRIDE_MAX[stride] - len(buf._nextptrs) >= entry_count:
            return buf
    buf = EUDJumpBuffer(stride)
    buf_list.append(buf)
    return buf


c.RegisterCreatePayloadCallback(_reset_jumpbuffers)


# Unused jump tables don't need to be allocated.
class JumpTriggerForward(c.ConstExpr):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(self, nextptrs) -> None:
        super().__init__()
        self._nextptrs = nextptrs
        self._stride = 4 if len(nextptrs) <= _STRIDE4_MAX else _STRIDE_LARGE
        self._jtb: EUDJumpBuffer | None = None

    def Evaluate(self):  # noqa: N802
        if self._jtb is None:
            self._jtb = _select_buffer(self._stride, len(self._nextptrs))
        try:
            return self._jtb._jdict[self].Evaluate()
        except KeyError:
            jt = self._jtb.create_jump_triggers(self, self._nextptrs)
            return jt.Evaluate()

