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

from collections.abc import Sequence
from random import random

from ... import utils as ut
from ...core.mapdata.chktok import CHK
from ...core.rawtrigger import AllPlayers, SetTo
from ...trigtrg import trigtrg as tt
from .btInliner import (
    GetExecutingPlayers,
    GetTriggerSize,
    InlineCodifyBinaryTrigger,
    InlineCodifyMultipleBinaryTriggers,
    TryToShareTrigger,
    tStartEnd,
)
from .ilccompile import CompileInlineCode, ComputeBaseInlineCodeGlobals

_inlineCodes: list[tuple[int, tStartEnd]] = []
_inliningRate: float = 1.0
_cutoffRate: list[float] = [1 + (i - 2) / 3 for i in range(9)]


def PRT_SetInliningRate(rate: float) -> None:
    """Set how much triggers will be inlined into STR section."""
    global _inliningRate
    _inliningRate = rate


def PreprocessInlineCode(chkt: CHK) -> None:
    global _inlineCodes
    trigSection = chkt.getsection("TRIG")
    _inlineCodes, trigSection = PreprocessTrigSection(trigSection)
    chkt.setsection("TRIG", trigSection)


def PreprocessTrigSection(trigSection: bytes) -> tuple[list[tuple[int, tStartEnd]], bytes]:
    """Fetch inline codes & compiles them"""
    ComputeBaseInlineCodeGlobals()
    if _inliningRate >= 1.0:
        return ConsecutiveInlineTrigSection(trigSection)

    inlineCodes: list[tuple[int, tStartEnd]] = []
    trigSegments: list[bytes] = []
    for i in range(0, len(trigSection), 2400):
        trigSegment = trigSection[i : i + 2400]
        if len(trigSegment) != 2400:
            continue

        propv = ut.b2i4(trigSegment, 320 + 2048)

        decoded = DispatchInlineCode(inlineCodes, trigSegment)
        if decoded:
            trigSegment = decoded

        elif propv < 0x80000000 and random() < _inliningRate:
            trigSegment = InlinifyNormalTrigger(inlineCodes, trigSegment)

        trigSegments.append(trigSegment)

    """
    This is rather hard to explain, but we need blank trigger.

    If inline_eudplib trigger is at the last of the trigger, then its
    nextptr should be modified to codeStart.

    But after flipprop works, RunTrigTrigger engine will re-change its nextptr
    to somewhere else, where everything quits.

    So we need 'normal' trigger at the last of TRIG triggers for every player.
    """
    trigSegments.append(tt.Trigger(players=[AllPlayers]))

    trigSection = b"".join(trigSegments)
    return inlineCodes, trigSection


def ConsecutiveInlineTrigSection(
    trigSection: bytes,
) -> tuple[list[tuple[int, tStartEnd]], bytes]:
    inlineCodes: list[tuple[int, tStartEnd]] = []
    trigSegments: list[bytes] = []
    pTriggers: tuple[
        list[bytes],
        list[bytes],
        list[bytes],
        list[bytes],
        list[bytes],
        list[bytes],
        list[bytes],
        list[bytes],
    ] = ([], [], [], [], [], [], [], [])

    def appendPTriggers(p):
        if pTriggers[p]:
            func = InlineCodifyMultipleBinaryTriggers(pTriggers[p])
            trigSegment = CreateInlineCodeDispatcher(inlineCodes, func, 1 << p)
            trigSegments.append(trigSegment)
            pTriggers[p].clear()

    for i in range(0, len(trigSection), 2400):
        trigSegment = trigSection[i : i + 2400]
        if len(trigSegment) != 2400:
            continue

        propv = ut.b2i4(trigSegment, 320 + 2048)
        playerExecutesTrigger = GetExecutingPlayers(trigSegment)

        decoded = DispatchInlineCode(inlineCodes, trigSegment)
        if decoded:
            trigSegment = decoded

        elif propv < 0x80000000:
            pCount = playerExecutesTrigger.count(True)
            if pCount >= 2:
                indexOrTrig = TryToShareTrigger(trigSegment)
                if isinstance(indexOrTrig, bytes):
                    size = GetTriggerSize(indexOrTrig)
                    if size * pCount * _cutoffRate[pCount] > 2400:
                        for p in range(8):
                            if playerExecutesTrigger[p]:
                                appendPTriggers(p)
                        trigSegments.append(indexOrTrig)
                        continue
            for p in range(8):
                if playerExecutesTrigger[p]:
                    pTriggers[p].append(trigSegment)
            continue
        for p in range(8):
            if playerExecutesTrigger[p]:
                appendPTriggers(p)
        trigSegments.append(trigSegment)
    for p in range(8):
        appendPTriggers(p)
    trigSegments.append(tt.Trigger(players=[AllPlayers]))

    trigSection = b"".join(trigSegments)
    return inlineCodes, trigSection


def GetInlineCodeList() -> list[tuple[int, tStartEnd]]:
    """Get list of compiled inline_eudplib code"""
    return _inlineCodes


def GetInlineCodePlayerList(bTrigger: bytes) -> int | None:
    # Check if effplayer & current_action is empty
    for player in range(28):
        if bTrigger[320 + 2048 + 4 + player] != 0:
            return None

    # trg.cond[0].condtype != 0
    if bTrigger[15] != 0:
        return None
    # trg.act[0].acttype != 0
    if bTrigger[346] != 0:
        return None

    return ut.b2i4(bTrigger, 24)


def DispatchInlineCode(
    inlineCodes: list[tuple[int, tStartEnd]], trigger_bytes: bytes
) -> bytearray | None:
    """Check if trigger segment has special data."""
    magicCode = ut.b2i4(trigger_bytes, 20)
    if magicCode != 0x10978D4A:
        return None

    playerCode = GetInlineCodePlayerList(trigger_bytes)
    if not playerCode:
        return None

    data = trigger_bytes[20:320] + trigger_bytes[352:2372]
    codeData = ut.b2u(data[8:]).rstrip("\0")

    # Compile code
    func = CompileInlineCode(codeData)
    return CreateInlineCodeDispatcher(inlineCodes, func, playerCode)


def InlinifyNormalTrigger(
    inlineCodes: list[tuple[int, tStartEnd]], trigger_bytes: bytes
) -> bytearray:
    """Inlinify normal binary triggers"""
    playerCode = 0
    for i in range(27):
        if trigger_bytes[320 + 2048 + 4 + i]:
            playerCode |= 1 << i

    func = InlineCodifyBinaryTrigger(trigger_bytes)
    return CreateInlineCodeDispatcher(inlineCodes, func, playerCode)


def CreateInlineCodeDispatcher(
    inlineCodes: list[tuple[int, tStartEnd]], func: tStartEnd, playerCode: int
) -> bytearray:
    """Create link from TRIG list to STR trigger."""
    funcID = len(inlineCodes) + 1024
    inlineCodes.append((funcID, func))

    # Return new trigger
    newTrigger = bytearray(2400)

    # Apply effplayer
    for player in range(27):
        if playerCode & (1 << player):
            newTrigger[320 + 2048 + 4 + player] = 1

    # Apply 4 SetDeaths
    SetDeathsTemplate = tt.SetDeaths(0, SetTo, 0, 0)
    newTrigger[320 + 32 * 0 : 320 + 32 * 1] = SetDeathsTemplate
    newTrigger[320 + 32 * 1 : 320 + 32 * 2] = SetDeathsTemplate
    newTrigger[320 + 32 * 2 : 320 + 32 * 3] = SetDeathsTemplate
    newTrigger[320 + 32 * 3 : 320 + 32 * 4] = SetDeathsTemplate

    # Apply flag
    newTrigger[0:4] = ut.i2b4(funcID)
    newTrigger[2368:2372] = b"\0\0\0\x10"

    return newTrigger
