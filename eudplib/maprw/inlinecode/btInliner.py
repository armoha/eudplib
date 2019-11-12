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


def TryToShareTrigger(bTrigger):
    playerExecutesTrigger = GetExecutingPlayers(bTrigger)
    if NoWaitAndPreserved(bTrigger) and playerExecutesTrigger.count(True) >= 2:
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
        for bTrigger in bTriggers:
            if isinstance(bTrigger, bytes):
                bTrigger = c.RawTrigger(trigSection=bTrigger)
                if firstTrigger is None:
                    firstTrigger = bTrigger
                nextTrigger << bTrigger
                nextTrigger = c.Forward()
                b2s = True
            elif isinstance(bTrigger, int):
                sTrigger = sharedTriggers[bTrigger]
                if isinstance(sTrigger, bytes):
                    sTrigger = c.RawTrigger(trigSection=sTrigger)
                    sharedTriggers[bTrigger] = sTrigger
                elif isinstance(sTrigger, c.RawTrigger):
                    if b2s:
                        c.SetNextTrigger(sTrigger)
                else:
                    raise TypeError()
                nextTrigger << sTrigger
                nextTrigger = c.Forward()
                tStartActions.append(c.SetNextPtr(sTrigger, nextTrigger))
                if firstTrigger is None:
                    firstTrigger = sTrigger
                b2s = False
            else:
                raise TypeError()
        tEnd = c.RawTrigger()
        nextTrigger << tEnd
    c.PopTriggerScope()

    if c.PushTriggerScope():
        tStart = c.Forward()
        tStart << c.NextTrigger()

        cs.DoActions(tStartActions)

        c.SetNextTrigger(firstTrigger)

    c.PopTriggerScope()

    return (tStart, tEnd)
