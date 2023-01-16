#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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

iHeader: bytes = os.urandom(16)
traceToolDataEPD = ut.EPD(Db(iHeader + bytes(4 * 2048)))
recordTraceAct = Forward()
PushTriggerScope()
recordTraceTrigger = RawTrigger(
    actions=[recordTraceAct << SetMemoryEPD(traceToolDataEPD + 4, SetTo, 0)]
)
PopTriggerScope()


def _f_initstacktrace() -> None:
    # Fill the header of trace stack with random string on runtime.
    # SC:R creates a copy of STR section during EUD emulation and writes to
    # only one of the copy during emulation stage. We should read the copy
    # that is really written in-game.
    # We will fill the trace stack 'magic code' on runtime, and later find the
    # magic code to locate the stack trace table.
    if not traceHeader:
        raise ut.EPError(_("Must call SaveMap first"))
    RawTrigger(
        actions=[
            SetMemoryEPD(traceToolDataEPD + 0, SetTo, ut.b2i4(traceHeader, 0x0)),
            SetMemoryEPD(traceToolDataEPD + 1, SetTo, ut.b2i4(traceHeader, 0x4)),
            SetMemoryEPD(traceToolDataEPD + 2, SetTo, ut.b2i4(traceHeader, 0x8)),
            SetMemoryEPD(traceToolDataEPD + 3, SetTo, ut.b2i4(traceHeader, 0xC)),
        ],
    )


def _EUDTracePush() -> None:
    RawTrigger(actions=SetMemory(recordTraceAct + 16, Add, 1))


def _EUDTracePop() -> None:
    EUDTraceLogRaw(0)
    RawTrigger(actions=SetMemory(recordTraceAct + 16, Subtract, 1))


nextTraceId = 0
traceMap: list[tuple[int, str]] = []
traceKey = 0
traceHeader: bytes = b""


def GetTraceStackDepth() -> EUDVariable:
    v = EUDVariable()
    v << 0
    for i in range(31, -1, -1):
        RawTrigger(
            conditions=MemoryX(recordTraceAct + 16, AtLeast, 1, 2**i),
            actions=v.AddNumber(2**i),
        )
    SeqCompute([(v, Subtract, traceToolDataEPD + 4)])
    return v


def _ResetTraceMap() -> None:
    """This function gets called by savemap.py::SaveMap to clear trace data."""
    global nextTraceId, traceKey, traceHeader
    nextTraceId = 0
    traceKey = ut.b2i4(os.urandom(4))
    traceMap.clear()
    traceHeader = os.urandom(16)


def EUDTraceLog(lineno: int | None = None) -> None:
    """Log trace."""
    global nextTraceId

    # Construct trace message from cpython stack
    # Note: we need to get the caller's filename, function name, and line no.
    # Using inspect module for this purpose is insanely slow, so we use
    # plain sys object with plain frame attributes.

    frame = sys._getframe(1)
    try:
        if lineno is None:
            lineno = frame.f_lineno
        msg = "%s|%s|%s" % (frame.f_code.co_filename, frame.f_code.co_name, lineno)
    finally:
        # frame object should be dereferenced as quickly as possible.
        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        del frame

    v = tracecrypt.mix(traceKey, nextTraceId)
    nextTraceId += 1
    if v == 0:  # We don't allow logging 0.
        v = tracecrypt.mix(traceKey, nextTraceId)
        nextTraceId += 1
    traceMap.append((v, str(msg)))

    EUDTraceLogRaw(v)


def EUDTraceLogRaw(v: int) -> None:
    nt = Forward()
    RawTrigger(
        nextptr=recordTraceTrigger,
        actions=[
            SetNextPtr(recordTraceTrigger, nt),
            SetMemory(recordTraceAct + 20, SetTo, v),
        ],
    )
    nt << NextTrigger()


def _GetTraceMap() -> tuple[tuple[bytes, bytes], list[tuple[int, str]]]:
    return (iHeader, traceHeader), traceMap
