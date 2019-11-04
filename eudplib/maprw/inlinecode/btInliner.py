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

    # 2. Create function body

    if c.PushTriggerScope():
        tStart = c.RawTrigger(actions=c.SetDeaths(0, c.SetTo, 0, 0))

        cp = _runner_cp
        execP = [p for p, e in enumerate(playerExecutesTrigger) if e]
        noWaitPreserve = True

        for i in range(64):
            actionbyte = bTrigger[320 + 32 * i + 26]
            if actionbyte in (4, 7):
                noWaitPreserve = False
                break
        
        if not bTrigger[320 + 2048] & 4:
            noWaitPreserve = False

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
