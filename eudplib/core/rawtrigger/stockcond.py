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

from ...localize import _
from ...utils import EPD, ep_assert, unProxy
from .condition import Condition
from .constenc import Kills  # for __calls__ binding
from .constenc import (
    EncodeComparison,
    EncodePlayer,
    EncodeResource,
    EncodeScore,
    EncodeSwitchState,
)
from .strenc import EncodeLocation, EncodeSwitch, EncodeUnit


def CountdownTimer(Comparison, Time) -> Condition:
    """Checks countdown timer.

    Example::

        CountdownTimer(AtLeast, 10)

    Memory Layout::

        0000 0000 0000 0000 TTTT TTTT 0000 CP01 0000

        T : Time, CP : Comparison.
    """
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)


def Command(Player, Comparison, Number, Unit) -> Condition:
    """[Player] commands [Comparison] [Number] [Unit].

    Example::
        Command(Player1, AtLeast, 30, "Terran Marine")


    """
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)


def Bring(Player, Comparison, Number, Unit, Location) -> Condition:
    """Player brings quantity units to location.

    This states that a player is required to bring ‘X’ number of units to a specific location. The units can be any player-controlled unit available in the game.
    """
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)


def Accumulate(Player, Comparison, Number, ResourceType) -> Condition:
    """Player accumulates quantity resources.

    Accumulate requires that the player gather enough of a specific resource.
    """
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)


# 'Kills' is already defined inside constenc, so we just add __call__ method
# to there instead of creating new function
def __Kills__internal(Player, Comparison, Number, Unit) -> Condition:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)


Kills._internalf = __Kills__internal


def CommandMost(Unit) -> Condition:
    """Current player commands the most units.

    Command the Most requires that you command the most of the defined units. These units can be any player-controlled unit available in the game. This condition compares all players in the game, including neutral and rescuable units.
    """
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)


def CommandMostAt(Unit, Location) -> Condition:
    """Current player commands the most units at location.

    Similar to the Command the Most, this condition compares the number of units at a specific location. The location can be restricted to certain elevations.
    """
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)


def MostKills(Unit) -> Condition:
    """Current player has most kills of unit.

    This condition is considered true if the trigger’s owner has the most kills of the specified Unit.
    """
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)


def HighestScore(ScoreType) -> Condition:
    """Current player has highest score points.

    This condition is considered true if the trigger’s owner has the highest Score. Note that if this is used as the only condition in a trigger, it will activate immediately at the start of the scenario, since all players will be tied for the highest score.
    """
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 9, ScoreType, 0)


def MostResources(ResourceType) -> Condition:
    """Current player has most resources.

    Similar to Most Kills, this condition is considered true if the trigger’s owner has the most of the specified resource.
    """
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)


def Switch(Switch, State) -> Condition:
    """Switch is set.

    This allows you to test against a switch value. Switches are on/off values that can be set with an action. Switches can be used to keep track of which triggers have been activated, to disable or enable certain triggers or to link multiple triggers together. You may also rename switches from this dialog box.
    """
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchState(State)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)


def ElapsedTime(Comparison, Time) -> Condition:
    """Elapsed scenario time is duration game seconds.

    This condition allows you to create triggers that occur after a specified number of game seconds have passed since the start of the scenario.
    """
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)


def Opponents(Player, Comparison, Number) -> Condition:
    """Player has quantity opponents remaining in the game.

    -   This condition evaluates how many of the players are opponents of the trigger owner. By default, all of the other players are considered opponents. A player does not count as an opponent if either of the following conditions are met:

    -   The player has been defeated. This condition only counts players that are still in the game.

    -   The player is set for allied victory with the trigger owner, AND the player is set for allied victory with all other players set for allied victory with the trigger owner. (The enemy of an ally is still an enemy.)

    As a result, if opponents equals zero, all of remaining players are set for allied victory with each other. Use this condition with the Victory action to create a scenario that allows for allied victory.
    """
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)


def Deaths(Player, Comparison, Number, Unit) -> Condition:
    """Player has suffered quantity deaths of unit.

    Gives you the ability to create actions that are launched when a player has suffered a specific number of deaths of any of the units in the game.
    """
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)


def CommandLeast(Unit) -> Condition:
    """Current player commands the least units.

    Command the Least allows you to define an action based on the player that commands the least units. You might use this to give advantages to slower players or to single out weakened players. Note that this condition checks all players, including neutral, computer controlled, and rescuable players.
    """
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)


def CommandLeastAt(Unit, Location) -> Condition:
    """Current player commands the least units at location.

    Command the Least At is similar to ‘Command the Least’, however, but only compares units at a particular location. The location can be restricted to certain elevations.
    """
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)


def LeastKills(Unit) -> Condition:
    """Current player has least kills of unit.

    This condition is considered true if the trigger’s owner has the least kills of the specified Unit.
    """
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)


def LowestScore(ScoreType) -> Condition:
    """Current player has lowest score points.

    This condition evaluates the current Score and is considered true if the current player has the lowest or is tied for the lowest score. Lowest Score checks all players, including neutral and rescuable players.
    """
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 19, ScoreType, 0)


def LeastResources(ResourceType) -> Condition:
    """Current player has least resources.

    Similar to Least Kills, this condition is considered true if the trigger’s owner has the least of the specified resource. Note that Least Resources checks all players, including neutral, computer controlled and rescuable players.
    """
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)


def Score(Player, ScoreType, Comparison, Number) -> Condition:
    """Player score type score is quantity.

    This condition allows you to analyze a player’s current Score and perform actions based on the value. You can reference any of the individual scoring types from score.
    """
    Player = EncodePlayer(Player)
    ScoreType = EncodeScore(ScoreType)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 21, ScoreType, 0)


def Always() -> Condition:
    """Always.

    Accumulate requires that the player gather enough of a specific resource.z
    """
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never() -> Condition:
    """Never.

    The Never condition can be used to temporarily disable actions for testing. A trigger with the Never condition will not activate at any point.
    """
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


def Memory(dest, cmptype, value) -> Condition:
    cmptype = EncodeComparison(cmptype)
    return Deaths(EPD(dest), cmptype, value, 0)


def MemoryEPD(dest, cmptype, value) -> Condition:
    cmptype = EncodeComparison(cmptype)
    return Deaths(dest, cmptype, value, 0)


def DeathsX(Player, Comparison, Number, Unit, Mask) -> Condition:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx=0x4353)


def MemoryX(dest, cmptype, value, mask) -> Condition:
    cmptype = EncodeComparison(cmptype)
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def MemoryXEPD(dest, cmptype, value, mask) -> Condition:
    cmptype = EncodeComparison(cmptype)
    return DeathsX(dest, cmptype, value, 0, mask)
