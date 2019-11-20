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


import random

from ... import core as c
from ... import ctrlstru as cs
from ... import eudlib as sf
from ...trigtrg.runtrigtrg import _runner_cp

sharedTriggers = []


def GetExecutingPlayers(bTrigger):
    # Get executing players of the trigger.
    # If all player executes it, then pass it
    if bTrigger[320 + 2048 + 4 + 17] != 0:
        playerExecutesTrigger = [True] * 8

    else:  # Should check manually
        playerExecutesTrigger = [False] * 8
        # By player
        for player in range(8):
            if bTrigger[320 + 2048 + 4 + player] != 0:
                playerExecutesTrigger[player] = True

        # By force
        playerForce = [0] * 8
        for player in range(8):
            playerForce[player] = c.GetPlayerInfo(player).force

        for force in range(4):
            if bTrigger[320 + 2048 + 4 + 18 + force] != 0:
                for player in range(8):
                    if playerForce[player] == force:
                        playerExecutesTrigger[player] = True
    return playerExecutesTrigger


def NoWaitAndPreserved(bTrigger):
    execOnce = True
    for i in range(64):
        actionbyte = bTrigger[320 + 32 * i + 26]
        if actionbyte in (4, 7):  # Wait or Transmission
            return False
        elif actionbyte == 3:  # PreserveTrigger
            execOnce = False
    if execOnce and not (bTrigger[320 + 2048] & 4):
        return False
    return True


def InlineCodifyBinaryTrigger(bTrigger):
    """ Inline codify raw(binary) trigger data.

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
            r = list(range(8))
            random.shuffle(r)
            for player in r:
                if playerExecutesTrigger[player]:
                    if cs.EUDSwitchCase()(player):
                        c.RawTrigger(trigSection=bTrigger)
                        cs.EUDBreak()

            cs.EUDEndSwitch()

            tEnd = c.RawTrigger()
    c.PopTriggerScope()

    return (tStart, tEnd)


def CountConditionsAndActions(bTrigger):
    cond_count, act_count = 0, 0
    for c in range(16):
        if bTrigger[c * 20 + 15] == 22:  # Always
            continue
        elif bTrigger[c * 20 + 15] >= 1:
            cond_count += 1
    for a in range(64):
        if bTrigger[320 + a * 32 + 26] in (3, 47):  # PreserveTrigger, Comment
            continue
        elif bTrigger[320 + a * 32 + 26] >= 1:
            act_count += 1
    return cond_count, act_count


def GetTriggerSize(bTrigger):
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

    for ret in range(min_size, 2408 // 4 + 1):
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


def TryToShareTrigger(bTrigger):
    if NoWaitAndPreserved(bTrigger):
        sharedTriggers.append(bTrigger)
        return len(sharedTriggers) - 1
    return bTrigger


def InlineCodifyMultipleBinaryTriggers(bTriggers):
    """ Inline codify raw(binary) trigger data.

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
            if isinstance(bTrigger, bytes):
                tEnd = c.RawTrigger(trigSection=bTrigger)
                nextTrigger << tEnd
                if i < len(bTriggers) - 1:
                    nextTrigger = c.Forward()
                b2s = True
            elif isinstance(bTrigger, int):
                tEnd = sharedTriggers[bTrigger]
                if isinstance(tEnd, bytes):
                    tEnd = c.RawTrigger(trigSection=tEnd)
                    sharedTriggers[bTrigger] = tEnd
                elif isinstance(tEnd, c.RawTrigger):
                    if b2s:
                        c.SetNextTrigger(tEnd)
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

    if c.PushTriggerScope():
        tStart = c.Forward()
        tStart << c.NextTrigger()

        cs.DoActions(tStartActions)

        c.SetNextTrigger(firstTrigger)

    c.PopTriggerScope()

    return (tStart, tEnd)
