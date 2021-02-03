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

from .condition import Condition
from .constenc import (
    EncodeComparison,
    EncodePlayer,
    EncodeResource,
    EncodeScore,
    EncodeSwitchState,
    Kills,  # for __calls__ binding
)

from .strenc import EncodeLocation, EncodeSwitch, EncodeUnit

from ...localize import _
from ...utils import EPD, ep_assert, unProxy


def CountdownTimer(Comparison, Time):
    """Checks countdown timer.

    Example::

        CountdownTimer(AtLeast, 10)

    Memory Layout::

        0000 0000 0000 0000 TTTT TTTT 0000 CP01 0000

        T : Time, CP : Comparison.
    """
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)


def Command(Player, Comparison, Number, Unit):
    """[Player] commands [Comparison] [Number] [Unit].

    Example::
        Command(Player1, AtLeast, 30, "Terran Marine")


    """
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)


def Bring(Player, Comparison, Number, Unit, Location):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)


def Accumulate(Player, Comparison, Number, ResourceType):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)


# 'Kills' is already defined inside constenc, so we just add __call__ method
# to there instead of creating new function
def __Kills__internal(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)


Kills._internalf = __Kills__internal


def CommandMost(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)


def CommandMostAt(Unit, Location):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)


def MostKills(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)


def HighestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 9, ScoreType, 0)


def MostResources(ResourceType):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)


def Switch(Switch, State):
    Switch = EncodeSwitch(Switch, issueError=True)
    State = EncodeSwitchState(State, issueError=True)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)


def ElapsedTime(Comparison, Time):
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)


def Opponents(Player, Comparison, Number):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)


def Deaths(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)


def CommandLeast(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)


def CommandLeastAt(Unit, Location):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)


def LeastKills(Unit):
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)


def LowestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 19, ScoreType, 0)


def LeastResources(ResourceType):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)


def Score(Player, ScoreType, Comparison, Number):
    Player = EncodePlayer(Player, issueError=True)
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    return Condition(0, Player, Number, 0, Comparison, 21, ScoreType, 0)


def Always():
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never():
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


def Memory(dest, cmptype, value):
    return Deaths(EPD(dest), cmptype, value, 0)


def MemoryEPD(dest, cmptype, value):
    return Deaths(dest, cmptype, value, 0)


def DeathsX(Player, Comparison, Number, Unit, Mask):
    Player = EncodePlayer(Player, issueError=True)
    Comparison = EncodeComparison(Comparison, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx="SC")


def MemoryX(dest, cmptype, value, mask):
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def MemoryXEPD(dest, cmptype, value, mask):
    return DeathsX(dest, cmptype, value, 0, mask)
