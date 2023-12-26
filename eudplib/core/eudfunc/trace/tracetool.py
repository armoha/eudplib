#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import sys

from .... import utils as ut
from ....localize import _
from ...allocator import Forward
from ...eudobj import Db
from ...rawtrigger import (
    Add,
    AtLeast,
    MemoryX,
    NextTrigger,
    PopTriggerScope,
    PushTriggerScope,
    RawTrigger,
    SetMemory,
    SetMemoryEPD,
    SetNextPtr,
    SetTo,
    Subtract,
)
from ...variable import EUDVariable, SeqCompute
from . import tracecrypt

i_header: bytes = os.urandom(16)
_tracetool_data_epd = ut.EPD(Db(i_header + bytes(4 * 2048)))
_record_trace_act = Forward()
PushTriggerScope()
_record_trace_trigger = RawTrigger(
    actions=[_record_trace_act << SetMemoryEPD(_tracetool_data_epd + 4, SetTo, 0)]
)
PopTriggerScope()


def _f_initstacktrace() -> None:
    # Fill the header of trace stack with random string on runtime.
    # SC:R creates a copy of STR section during EUD emulation and writes to
    # only one of the copy during emulation stage. We should read the copy
    # that is really written in-game.
    # We will fill the trace stack 'magic code' on runtime, and later find the
    # magic code to locate the stack trace table.
    if not trace_header:
        raise ut.EPError(_("Must call SaveMap first"))
    RawTrigger(
        actions=[
            SetMemoryEPD(_tracetool_data_epd + 0, SetTo, ut.b2i4(trace_header, 0x0)),
            SetMemoryEPD(_tracetool_data_epd + 1, SetTo, ut.b2i4(trace_header, 0x4)),
            SetMemoryEPD(_tracetool_data_epd + 2, SetTo, ut.b2i4(trace_header, 0x8)),
            SetMemoryEPD(_tracetool_data_epd + 3, SetTo, ut.b2i4(trace_header, 0xC)),
        ],
    )


def _eud_trace_push() -> None:
    RawTrigger(actions=SetMemory(_record_trace_act + 16, Add, 1))


def _eud_trace_pop() -> None:
    _eud_trace_log_raw(0)
    RawTrigger(actions=SetMemory(_record_trace_act + 16, Subtract, 1))


_next_trace_id = 0
trace_map: list[tuple[int, str]] = []
_trace_key = 0
trace_header: bytes = b""


def GetTraceStackDepth() -> EUDVariable:  # noqa: N802
    v = EUDVariable()
    v << 0
    for i in range(31, -1, -1):
        RawTrigger(
            conditions=MemoryX(_record_trace_act + 16, AtLeast, 1, 2**i),
            actions=v.AddNumber(2**i),
        )
    SeqCompute([(v, Subtract, _tracetool_data_epd + 4)])
    return v


def _reset_trace_map() -> None:
    """This function gets called by savemap.py::SaveMap to clear trace data."""
    global _next_trace_id, _trace_key, trace_header
    _next_trace_id = 0
    _trace_key = ut.b2i4(os.urandom(4))
    trace_map.clear()
    trace_header = os.urandom(16)


def EUDTraceLog(lineno: int | None = None) -> None:  # noqa: N802
    """Log trace."""
    global _next_trace_id

    # Construct trace message from cpython stack
    # Note: we need to get the caller's filename, function name, and line no.
    # Using inspect module for this purpose is insanely slow, so we use
    # plain sys object with plain frame attributes.

    frame = sys._getframe(1)
    try:
        if lineno is None:
            lineno = frame.f_lineno
        msg = f"{frame.f_code.co_filename}|{frame.f_code.co_name}|{lineno}"
    finally:
        # frame object should be dereferenced as quickly as possible.
        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        del frame

    v = tracecrypt.mix(_trace_key, _next_trace_id)
    _next_trace_id += 1
    if v == 0:  # We don't allow logging 0.
        v = tracecrypt.mix(_trace_key, _next_trace_id)
        _next_trace_id += 1
    trace_map.append((v, str(msg)))

    _eud_trace_log_raw(v)


def _eud_trace_log_raw(v: int) -> None:
    nt = Forward()
    RawTrigger(
        nextptr=_record_trace_trigger,
        actions=[
            SetNextPtr(_record_trace_trigger, nt),
            SetMemory(_record_trace_act + 20, SetTo, v),
        ],
    )
    nt << NextTrigger()


def _get_trace_map() -> tuple[tuple[bytes, bytes], list[tuple[int, str]]]:
    return (i_header, trace_header), trace_map
