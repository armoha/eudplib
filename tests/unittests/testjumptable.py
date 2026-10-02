from random import sample

from helper import *

import eudplib.ctrlstru.jumptable as _jt
from eudplib.bindings._rust import allocator as _alc
from eudplib.ctrlstru.jumptable import (
    _LFLAGS_OFFSET,
    _STRIDE4_MAX,
    _STRIDE_LARGE,
    EUDJumpBuffer,
    JumpTriggerForward,
)


class _MockBuf:
    """Mimics the payload-buffer write interface and builds a byte image."""

    def __init__(self):
        self.data = bytearray()

    def WriteByte(self, v):  # noqa: N802
        self.data.append(int(v) & 0xFF)

    def WriteWord(self, v):  # noqa: N802
        self.data += int(v).to_bytes(2, "little")

    def WriteDword(self, v):  # noqa: N802
        self.data += int(v).to_bytes(4, "little")

    def WriteSpace(self, n):  # noqa: N802
        self.data += bytearray(n)

    def WriteBytes(self, b):  # noqa: N802
        self.data += bytes(b)


@TestInstance
def test_jumptable_structure():
    # Stride selection: <= 593 entries -> S=4, >= 594 entries -> S=8
    assert JumpTriggerForward([0])._stride == 4
    assert JumpTriggerForward([0] * _STRIDE4_MAX)._stride == 4
    assert JumpTriggerForward([0] * (_STRIDE4_MAX + 1))._stride == _STRIDE_LARGE
    assert JumpTriggerForward([0] * 2000)._stride == _STRIDE_LARGE

    # Stride validation: only 4 and 8 are allowed
    for bad in (1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16):
        with expect_eperror():
            EUDJumpBuffer(bad)

    # S=4 capacity: more than 593 entries are rejected
    with expect_eperror():
        b4full = EUDJumpBuffer(4)
        b4full.create_jump_triggers("v", [0] * (_STRIDE4_MAX + 1))
    b4part = EUDJumpBuffer(4)
    b4part.create_jump_triggers("v", [0] * 100)
    with expect_eperror():
        b4part.create_jump_triggers("v", [0] * (_STRIDE4_MAX - 99))

    # S=4 layout: nextptr at 4k, lFlags = TF_COMPLETE(8) at 4k + 2372
    b4 = EUDJumpBuffer(4)
    b4._nextptrs = list(range(7))
    assert b4.GetDataSize() == _LFLAGS_OFFSET + 4 * 7
    m = _MockBuf()
    b4.WritePayload(m)
    assert len(m.data) == b4.GetDataSize()
    for k in range(7):
        assert m.data[4 * k : 4 * k + 4] == k.to_bytes(4, "little")
        assert (
            m.data[4 * k + _LFLAGS_OFFSET : 4 * k + _LFLAGS_OFFSET + 4]
            == (8).to_bytes(4, "little")
        )

    # S=8 layout: nextptr at 8k, lFlags = TF_COMPLETE(8) at 8k + 2372
    b8 = EUDJumpBuffer(_STRIDE_LARGE)
    b8._nextptrs = list(range(600))
    assert b8.GetDataSize() == _LFLAGS_OFFSET + _STRIDE_LARGE * 600
    m = _MockBuf()
    b8.WritePayload(m)
    assert len(m.data) == b8.GetDataSize()
    for k in range(600):
        assert m.data[8 * k : 8 * k + 4] == k.to_bytes(4, "little")
        assert (
            m.data[8 * k + _LFLAGS_OFFSET : 8 * k + _LFLAGS_OFFSET + 4]
            == (8).to_bytes(4, "little")
        )

    # Buffer packing: prefer filling an existing S=4 buffer over a new one
    saved4, saved8 = _jt._jtb4, _jt._jtb8
    _jt._reset_jumpbuffers()
    try:
        b1 = _jt._select_buffer(4, 100)
        b1._nextptrs.extend([0] * 100)  # fill 100 entries
        b2 = _jt._select_buffer(4, 200)  # room (493) >= 200 -> reuse b1
        assert b1 is b2
        b1._nextptrs.extend([0] * 200)  # 300 entries in b1 now
        b3 = _jt._select_buffer(4, 400)  # room (293) < 400 -> new buffer
        assert b3 is not b1
        a1 = _jt._select_buffer(_STRIDE_LARGE, 600)
        a2 = _jt._select_buffer(_STRIDE_LARGE, 700)  # S=8 unbounded -> share
        assert a1 is a2
    finally:
        _jt._jtb4, _jt._jtb8 = saved4, saved8

    # Allocator integration: occupancy length == GetDataSize and the written
    # bytes land at the expected positions (no overlap between buffers)
    pb = _alc.PayloadBuilder()
    bb4 = EUDJumpBuffer(4)
    bb4._nextptrs = list(range(50))
    bb8 = EUDJumpBuffer(_STRIDE_LARGE)
    bb8._nextptrs = list(range(600))
    found = {bb4: 0, bb8: 1}
    pb.alloc_objects(found)
    payload, _, _ = pb.construct_payload(found)
    for buf, idx in ((bb4, 0), (bb8, 1)):
        addr = pb.get_object_addr(idx).offset
        stride = buf._stride
        for k in range(len(buf._nextptrs)):
            v = int(buf._nextptrs[k])
            assert payload[addr + stride * k : addr + stride * k + 4] == v.to_bytes(
                4, "little"
            )
            assert (
                payload[
                    addr + stride * k + _LFLAGS_OFFSET :
                    addr + stride * k + _LFLAGS_OFFSET + 4
                ]
                == (8).to_bytes(4, "little")
            )


@TestInstance
def test_jumptable_small_switch():
    # Dense 16-case switch (16 keys) -> S=4 jump table
    @EUDFunc
    def small(x):
        ret = EUDVariable()
        ret << 0
        EUDSwitch(x)
        for case in range(16):
            if EUDSwitchCase()(case):
                ret << case * 7
                EUDBreak()
        if EUDSwitchDefault()():
            ret << -1
        EUDEndSwitch()
        return ret

    for probe in (0, 1, 7, 15):
        test_equality(f"S4 switch probe {probe}", small(probe), probe * 7)


@TestInstance
def test_jumptable_large_switch():
    # 600-case switch -> S=8 jump table (600 > 593)
    cases = sorted(sample(range(1024), 600))
    caseset = set(cases)
    miss = next(v for v in range(1024) if v not in caseset)

    @EUDFunc
    def large(x):
        ret = EUDVariable()
        ret << 0
        EUDSwitch(x)
        for case in cases:
            if EUDSwitchCase()(case):
                ret << case * 3
                EUDBreak()
        if EUDSwitchDefault()():
            ret << -1
        EUDEndSwitch()
        return ret

    probes = [*cases[:3], cases[300], cases[-1], miss]
    for probe in probes:
        expected = probe * 3 if probe in caseset else -1
        test_equality(f"S8 switch probe {probe}", large(probe), expected)
