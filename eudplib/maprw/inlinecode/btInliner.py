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


from collections.abc import ByteString, Collection
from typing import TypeAlias

from ... import core as c
from ... import ctrlstru as cs
from ... import eudlib as sf
from ... import utils as ut
from ...trigtrg.runtrigtrg import _runner_cp

sharedTriggers: list[bytes | c.RawTrigger] = []
tStartEnd: TypeAlias = tuple[c.ConstExpr, c.RawTrigger]


def GetExecutingPlayers(
    bTrigger: bytes,
) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
    # Get executing players of the trigger.
    # If AllPlayers executes it, then pass it
    if bTrigger[320 + 2048 + 4 + 17] != 0:
        return (True,) * 8
    # Should check manually, by player and force
    return tuple(
        (
            bool(bTrigger[320 + 2048 + 4 + player])
            or bool(bTrigger[320 + 2048 + 4 + 18 + c.GetPlayerInfo(player).force])
        )
        for player in range(8)
    )  # type: ignore


def NoWaitAndPreserved(bTrigger: ByteString) -> bool:
    execOnce = True
    for i in range(64):
        actionflag = bTrigger[320 + 32 * i + 28]
        if not actionflag & 0b10:  # Enabled Flag
            continue
        actionbyte = bTrigger[320 + 32 * i + 26]
        if actionbyte in (4, 7):  # Wait or Transmission
            return False
        elif actionbyte == 3:  # PreserveTrigger
            execOnce = False
    if execOnce and not (bTrigger[320 + 2048] & 4):
        return False
    return True


def InlineCodifyBinaryTrigger(bTrigger: bytes) -> tStartEnd:
    """Inline codify raw(binary) trigger data.

    For minimal protection, eudplib make some of the trig-triggers to
    eudplib trigger. This function makes eudplib trigger out of raw
    binary trigger stream.

    :param bTrigger: Binary trigger data
    :returns: (tStart, tEnd) pair, as being used by tEnd
    """

    # 1. Get executing players of the trigger.
    # If all player executes it, then pass it
    playerExecutesTrigger = GetExecutingPlayers(bTrigger)

    # 2. Create function body

    if c.PushTriggerScope():
        tStart = c.RawTrigger(actions=c.SetDeaths(0, c.SetTo, 0, 0))

        cp = _runner_cp
        execP = [p for p, e in enumerate(playerExecutesTrigger) if e]
        noWaitPreserve = NoWaitAndPreserved(bTrigger)

        if noWaitPreserve and len(execP) == 8:
            tEnd = c.RawTrigger(trigSection=bTrigger)
        if noWaitPreserve and max(execP) - min(execP) == len(execP) - 1:
            if cs.EUDIf()([cp >= min(execP), cp <= max(execP)]):
                c.RawTrigger(trigSection=bTrigger)
            cs.EUDEndIf()
            tEnd = c.RawTrigger()
        else:
            cs.EUDSwitch(cp)
            for player in ut.RandList(range(8)):
                if playerExecutesTrigger[player]:
                    if cs.EUDSwitchCase()(player):
                        c.RawTrigger(trigSection=bTrigger)
                        cs.EUDBreak()

            cs.EUDEndSwitch()

            tEnd = c.RawTrigger()
    c.PopTriggerScope()

    return tStart, tEnd


def CountConditionsAndActions(bTrigger: bytes) -> tuple[int, int]:
    cond_count, act_count = 0, 0
    for c in range(16):
        if bTrigger[c * 20 + 15] == 22:  # Always
            continue
        elif bTrigger[c * 20 + 15] >= 1:
            cond_count += 1
    for a in range(64):
        if bTrigger[320 + a * 32 + 26] in (47,):  # Comment
            continue
        elif bTrigger[320 + a * 32 + 26] >= 1:
            act_count += 1
    return cond_count, act_count


def GetTriggerSize(bTrigger: bytes) -> int:
    cond_count, act_count = CountConditionsAndActions(bTrigger)
    min_size = 4 + 5 * cond_count + 8 * act_count
    trig = {
        "n": [1],  # nextptr
        "P": [594],  # preserved
        "C": list(range(2, 2 + 5 * cond_count)),  # conditions
        "c": [5 + 5 * cond_count],  # condtype == 0
        "A": list(range(82, 82 + 8 * act_count)),  # actions
        "a": [88 + 8 * act_count],  # acttype == 0
    }
    if cond_count == 16:
        del trig["c"]
    if act_count == 64:
        del trig["a"]

    for ret in range(min_size, 2408 // 4):
        output = ["_" for _ in range(ret)]

        def _f():
            for k, v in trig.items():
                for x in v:
                    if output[x % ret] != "_":
                        return False
                    output[x % ret] = k
            return True

        if _f():
            return ret * 4
    return 2408


def TryToShareTrigger(bTrigger: bytes) -> int | bytes:
    if NoWaitAndPreserved(bTrigger):
        sharedTriggers.append(bTrigger)
        return len(sharedTriggers) - 1
    return bTrigger


def InlineCodifyMultipleBinaryTriggers(
    bTriggers: Collection[bytes | int],
) -> tStartEnd:
    """Inline codify raw(binary) trigger data.

    For minimal protection, eudplib make some of the trig-triggers to
    eudplib trigger. This function makes eudplib trigger out of raw
    binary trigger stream.

    :param bTrigger: Binary trigger data
    :returns: (tStart, tEnd) pair, as being used by tEnd
    """

    # Create function body

    firstTrigger = None
    tStartActions = [c.SetDeaths(0, c.SetTo, 0, 0)]
    b2s = False

    if c.PushTriggerScope():
        nextTrigger = c.Forward()
        for i, bTrigger in enumerate(bTriggers):
            tEnd: c.RawTrigger
            if isinstance(bTrigger, bytes):
                tEnd = c.RawTrigger(trigSection=bTrigger)
                nextTrigger << tEnd
                if i < len(bTriggers) - 1:
                    nextTrigger = c.Forward()
                b2s = True
            elif isinstance(bTrigger, int):
                sharedTrigger = sharedTriggers[bTrigger]
                if isinstance(sharedTrigger, bytes):
                    tEnd = c.RawTrigger(trigSection=sharedTrigger)
                    sharedTriggers[bTrigger] = tEnd
                elif isinstance(sharedTrigger, c.RawTrigger):
                    tEnd = sharedTrigger
                    if b2s:
                        c.SetNextTrigger(sharedTrigger)
                else:
                    raise TypeError()
                nextTrigger << tEnd
                if i < len(bTriggers) - 1:
                    nextTrigger = c.Forward()
                    tStartActions.append(c.SetNextPtr(tEnd, nextTrigger))
                b2s = False
            else:
                raise TypeError()
            if firstTrigger is None:
                firstTrigger = tEnd
    c.PopTriggerScope()

    if firstTrigger is None:
        raise TypeError()

    if c.PushTriggerScope():
        tStart = c.Forward()
        tStart << c.NextTrigger()

        cs.DoActions(tStartActions)

        c.SetNextTrigger(firstTrigger)

    c.PopTriggerScope()

    return tStart, tEnd
