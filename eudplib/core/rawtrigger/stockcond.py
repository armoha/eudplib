#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...utils import EPD
from .condition import Condition
from .constenc import (
    Comparison,
    Dword,
    EncodeComparison,
    EncodePlayer,
    EncodeResource,
    EncodeScore,
    EncodeSwitchState,
    Kills,  # for __calls__ binding
    Player,
    Resource,
    SwitchState,
)
from .constenc import Score as _Score
from .strenc import EncodeLocation, EncodeSwitch, EncodeUnit, Location, Unit
from .strenc import Switch as _Switch


def CountdownTimer(comparison: Comparison, time: Dword) -> Condition:  # noqa: N802
    """Checks countdown timer.

    Example::

        CountdownTimer(AtLeast, 10)

    Memory Layout::

        0000 0000 0000 0000 TTTT TTTT 0000 CP01 0000

        T : time, CP : Comparison.
    """
    comparison = EncodeComparison(comparison)
    return Condition(0, 0, time, 0, comparison, 1, 0, 0)


def Command(  # noqa: N802
    player: Player, comparison: Comparison, number: Dword, unit: Unit
) -> Condition:
    """[Player] commands [Comparison] [Number] [Unit].

    Example::
        Command(Player1, AtLeast, 30, "Terran Marine")


    """
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 2, 0, 0)


def Bring(  # noqa: N802
    player: Player,
    comparison: Comparison,
    number: Dword,
    unit: Unit,
    location: Location,
) -> Condition:
    """Player brings quantity units to location.

    This states that a player is required to bring 'X' number of units to a
    specific location. The units can be any player-controlled unit available
    in the game.
    """
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, player, number, unit, comparison, 3, 0, 0)


def Accumulate(  # noqa: N802
    player: Player,
    comparison: Comparison,
    number: Dword,
    resource_type: Resource,
) -> Condition:
    """Player accumulates quantity resources.

    Accumulate requires that the player gather enough of a specific resource.
    """
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    resource_type = EncodeResource(resource_type)
    return Condition(0, player, number, 0, comparison, 4, resource_type, 0)


# 'Kills' is already defined inside constenc, so we just add __call__ method
# to there instead of creating new function
def __kills__internal(
    player: Player, comparison: Comparison, number: Dword, unit: Unit
) -> Condition:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 5, 0, 0)


Kills._internalf = __kills__internal


def CommandMost(unit: Unit) -> Condition:  # noqa: N802
    """Current player commands the most units.

    Command the Most requires that you command the most of the defined units.
    These units can be any player-controlled unit available in the game.
    This condition compares all players in the game, including neutral and
    rescuable units.
    """
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 6, 0, 0)


def CommandMostAt(unit: Unit, location: Location) -> Condition:  # noqa: N802
    """Current player commands the most units at location.

    Similar to the Command the Most, this condition compares
    the number of units at a specific location.
    The location can be restricted to certain elevations.
    """
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, 0, 0, unit, 0, 7, 0, 0)


def MostKills(unit: Unit) -> Condition:  # noqa: N802
    """Current player has most kills of unit.

    This condition is considered true if the trigger's owner has
    the most kills of the specified Unit.
    """
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 8, 0, 0)


def HighestScore(ScoreType: _Score) -> Condition:  # noqa: N802, N803
    """Current player has highest score points.

    This condition is considered true if the trigger's owner has the highest
    Score. Note that if this is used as the only condition in a trigger,
    it will activate immediately at the start of the scenario,
    since all players will be tied for the highest score.
    """
    score_type = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 9, score_type, 0)


def MostResources(resource_type: Resource) -> Condition:  # noqa: N802
    """Current player has most resources.

    Similar to Most Kills, this condition is considered true if the trigger's
    owner has the most of the specified resource.
    """
    resource_type = EncodeResource(resource_type)
    return Condition(0, 0, 0, 0, 0, 10, resource_type, 0)


def Switch(switch: _Switch, state: SwitchState) -> Condition:  # noqa: N802
    """Switch is set.

    This allows you to test against a switch value. Switches are on/off values
    that can be set with an action.
    Switches can be used to keep track of which triggers have been activated,
    to disable or enable certain triggers or to link multiple triggers
    together. You may also rename switches from this dialog box.
    """
    switch = EncodeSwitch(switch)
    state = EncodeSwitchState(state)
    return Condition(0, 0, 0, 0, state, 11, switch, 0)


def ElapsedTime(comparison: Comparison, time: Dword) -> Condition:  # noqa: N802
    """Elapsed scenario time is duration game seconds.

    This condition allows you to create triggers that occur after a specified
    number of game seconds have passed since the start of the scenario.
    """
    comparison = EncodeComparison(comparison)
    return Condition(0, 0, time, 0, comparison, 12, 0, 0)


def Opponents(  # noqa: N802
    player: Player, comparison: Comparison, number: Dword
) -> Condition:
    """Player has quantity opponents remaining in the game.

    This condition evaluates how many of the players are opponents of the
    trigger owner. By default, all of the other players are considered
    opponents. A player does not count as an opponent if either of the
    following conditions are met:

    * The player has been defeated. This condition only counts players
    that are still in the game.

    * The player is set for allied victory with the trigger owner,
    AND the player is set for allied victory with all other players set for
    allied victory with the trigger owner.
    (The enemy of an ally is still an enemy.)

    As a result, if opponents equals zero, all of remaining players are set for
    allied victory with each other. Use this condition with the Victory action
    to create a scenario that allows for allied victory.
    """
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    return Condition(0, player, number, 0, comparison, 14, 0, 0)


def Deaths(  # noqa: N802
    player: Player, comparison: Comparison, number: Dword, unit: Unit
) -> Condition:
    """Player has suffered quantity deaths of unit.

    Gives you the ability to create actions that are launched when a player has
    suffered a specific number of deaths of any of the units in the game.
    """
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 15, 0, 0)


def CommandLeast(unit: Unit) -> Condition:  # noqa: N802
    """Current player commands the least units.

    Command the Least allows you to define an action based on the player that
    commands the least units. You might use this to give advantages to slower
    players or to single out weakened players. Note that this condition checks
    all players, including neutral, computer controlled, and rescuable players.
    """
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 16, 0, 0)


def CommandLeastAt(unit: Unit, location: Location) -> Condition:  # noqa: N802
    """Current player commands the least units at location.

    Command the Least At is similar to 'Command the Least', however, but only
    compares units at a particular location.
    The location can be restricted to certain elevations.
    """
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, 0, 0, unit, 0, 17, 0, 0)


def LeastKills(unit: Unit) -> Condition:  # noqa: N802
    """Current player has least kills of unit.

    This condition is considered true if the trigger's owner has the least
    kills of the specified Unit.
    """
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 18, 0, 0)


def LowestScore(ScoreType: _Score) -> Condition:  # noqa: N802, N803
    """Current player has lowest score points.

    This condition evaluates the current Score and is considered true
    if the current player has the lowest or is tied for the lowest score.
    Lowest Score checks all players, including neutral and rescuable players.
    """
    score_type = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 19, score_type, 0)


def LeastResources(resource_type: Resource) -> Condition:  # noqa: N802
    """Current player has least resources.

    Similar to Least Kills, this condition is considered true if the trigger's
    owner has the least of the specified resource.
    Note that Least Resources checks all players, including neutral, computer
    controlled and rescuable players.
    """
    resource_type = EncodeResource(resource_type)
    return Condition(0, 0, 0, 0, 0, 20, resource_type, 0)


def Score(  # noqa: N802
    player: Player,
    ScoreType: _Score,  # noqa: N803
    comparison: Comparison,
    number: Dword,
) -> Condition:
    """Player score type score is quantity.

    This condition allows you to analyze a player's current Score and perform
    actions based on the value.
    You can reference any of the individual scoring types from score.
    """
    player = EncodePlayer(player)
    score_type = EncodeScore(ScoreType)
    comparison = EncodeComparison(comparison)
    return Condition(0, player, number, 0, comparison, 21, score_type, 0)


def Always() -> Condition:  # noqa: N802
    """Always.

    Accumulate requires that the player gather enough of a specific resource.
    """
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never() -> Condition:  # noqa: N802
    """Never.

    The Never condition can be used to temporarily disable actions for testing.
    A trigger with the Never condition will not activate at any point.
    """
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


def Memory(dest: Dword, cmptype: Comparison, value: Dword) -> Condition:  # noqa: N802
    comparison = EncodeComparison(cmptype)
    return Deaths(EPD(dest), comparison, value, 0)


def MemoryEPD(dest: Dword, cmptype: Comparison, value: Dword) -> Condition:  # noqa: N802
    comparison = EncodeComparison(cmptype)
    return Deaths(dest, comparison, value, 0)


def DeathsX(  # noqa: N802
    player: Player,
    comparison: Comparison,
    number: Dword,
    unit: Unit,
    mask: Dword,
) -> Condition:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(
        mask, player, number, unit, comparison, 15, 0, 0, eudx=0x4353
    )


def MemoryX(  # noqa: N802
    dest: Dword, cmptype: Comparison, value: Dword, mask: Dword
) -> Condition:
    comparison = EncodeComparison(cmptype)
    return DeathsX(EPD(dest), comparison, value, 0, mask)


def MemoryXEPD(  # noqa: N802
    dest: Dword, cmptype: Comparison, value: Dword, mask: Dword
) -> Condition:
    comparison = EncodeComparison(cmptype)
    return DeathsX(dest, comparison, value, 0, mask)
