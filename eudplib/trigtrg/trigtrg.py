# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from struct import pack
from typing import TypeAlias

from ..core import UnitProperty

# re-export stuffs
from ..core.rawtrigger.constenc import Add as Add
from ..core.rawtrigger.constenc import All as All
from ..core.rawtrigger.constenc import AlliedVictory as AlliedVictory
from ..core.rawtrigger.constenc import Ally as Ally
from ..core.rawtrigger.constenc import AtLeast as AtLeast
from ..core.rawtrigger.constenc import AtMost as AtMost
from ..core.rawtrigger.constenc import Attack as Attack
from ..core.rawtrigger.constenc import Buildings as Buildings
from ..core.rawtrigger.constenc import Clear as Clear
from ..core.rawtrigger.constenc import Cleared as Cleared
from ..core.rawtrigger.constenc import Custom as Custom
from ..core.rawtrigger.constenc import Disable as Disable
from ..core.rawtrigger.constenc import Enable as Enable
from ..core.rawtrigger.constenc import (
    EncodeAllyStatus,
    EncodeComparison,
    EncodeCount,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSwitchAction,
    EncodeSwitchState,
    TrgAllyStatus,
    TrgComparison,
    TrgCount,
    TrgModifier,
    TrgOrder,
    TrgPropState,
    TrgResource,
    TrgScore,
    TrgSwitchAction,
    TrgSwitchState,
    _Kills,
)
from ..core.rawtrigger.constenc import Enemy as Enemy
from ..core.rawtrigger.constenc import Exactly as Exactly
from ..core.rawtrigger.constenc import Gas as Gas
from ..core.rawtrigger.constenc import KillsAndRazings as KillsAndRazings
from ..core.rawtrigger.constenc import Move as Move
from ..core.rawtrigger.constenc import Ore as Ore
from ..core.rawtrigger.constenc import OreAndGas as OreAndGas
from ..core.rawtrigger.constenc import Patrol as Patrol
from ..core.rawtrigger.constenc import Random as Random
from ..core.rawtrigger.constenc import Razings as Razings
from ..core.rawtrigger.constenc import Set as Set
from ..core.rawtrigger.constenc import SetTo as SetTo
from ..core.rawtrigger.constenc import Subtract as Subtract
from ..core.rawtrigger.constenc import Toggle as Toggle
from ..core.rawtrigger.constenc import Total as Total
from ..core.rawtrigger.constenc import Units as Units
from ..core.rawtrigger.constenc import UnitsAndBuildings as UnitsAndBuildings
from ..core.rawtrigger.strenc import (
    EncodeAIScript,
    EncodeLocation,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
)
from ..scdata.player import P1 as P1
from ..scdata.player import P2 as P2
from ..scdata.player import P3 as P3
from ..scdata.player import P4 as P4
from ..scdata.player import P5 as P5
from ..scdata.player import P6 as P6
from ..scdata.player import P7 as P7
from ..scdata.player import P8 as P8
from ..scdata.player import P9 as P9
from ..scdata.player import P10 as P10
from ..scdata.player import P11 as P11
from ..scdata.player import P12 as P12
from ..scdata.player import Allies as Allies
from ..scdata.player import AllPlayers as AllPlayers
from ..scdata.player import CurrentPlayer as CurrentPlayer
from ..scdata.player import Foes as Foes
from ..scdata.player import Force1 as Force1
from ..scdata.player import Force2 as Force2
from ..scdata.player import Force3 as Force3
from ..scdata.player import Force4 as Force4
from ..scdata.player import NeutralPlayers as NeutralPlayers
from ..scdata.player import (
    NonAlliedVictoryPlayers as NonAlliedVictoryPlayers,
)
from ..scdata.player import Player1 as Player1
from ..scdata.player import Player2 as Player2
from ..scdata.player import Player3 as Player3
from ..scdata.player import Player4 as Player4
from ..scdata.player import Player5 as Player5
from ..scdata.player import Player6 as Player6
from ..scdata.player import Player7 as Player7
from ..scdata.player import Player8 as Player8
from ..scdata.player import Player9 as Player9
from ..scdata.player import Player10 as Player10
from ..scdata.player import Player11 as Player11
from ..scdata.player import Player12 as Player12
from ..scdata.player import TrgPlayer
from ..utils import EPD, FlattenList, ep_assert

"""
Defines stock conditions & actions. You are most likely to use only conditions
declared in this file. This file also serves as a basic reference for trigger
condition / actions.

 ex) You want to create 'Create Unit' action:
   1. Remove spaces. 'CreateUnit'
   2. Find 'CreateUnit' in this file. You'll see the following function def.
     def CreateUnit(Number, unit, where, for_player):
   3. Make your action as mentioned here.
     ex) CreateUnit(30, 'Terran Marine', 'Anywhere', Player1)
"""
AllyStatus: TypeAlias = TrgAllyStatus | int
Comparison: TypeAlias = TrgComparison | int
Count: TypeAlias = TrgCount | int
Modifier: TypeAlias = TrgModifier | int
_Order: TypeAlias = TrgOrder | int
Player: TypeAlias = TrgPlayer | int
PropState: TypeAlias = TrgPropState | int
Resource: TypeAlias = TrgResource | int
_Score: TypeAlias = TrgScore | int
SwitchAction: TypeAlias = TrgSwitchAction | int
SwitchState: TypeAlias = TrgSwitchState | int

Unit: TypeAlias = str | int | bytes
Location: TypeAlias = str | int | bytes
String: TypeAlias = str | int | bytes
AIScript: TypeAlias = str | int | bytes
_Switch: TypeAlias = str | int | bytes


def Condition(  # noqa: N802
    locid: int,
    player: int,
    amount: int,
    unitid: int,
    comparison: int,
    condtype: int,
    restype: int,
    flag: int,
    *,
    eudx: int = 0,
) -> bytes:
    if player < 0:
        player += 0x100000000  # EPD

    player &= 0xFFFFFFFF
    amount &= 0xFFFFFFFF

    return pack(
        "<IIIHBBBBH",
        locid,
        player,
        amount,
        unitid,
        comparison,
        condtype,
        restype,
        flag,
        eudx,
    )


def Action(  # noqa: N802
    locid1: int,
    strid: int,
    wavid: int,
    time: int,
    player1: int,
    player2: int,
    unitid: int,
    acttype: int,
    amount: int,
    flags: int,
    *,
    eudx: int = 0,
) -> bytes:
    if player1 < 0:
        player1 += 0x100000000  # EPD
    if player2 < 0:
        player2 += 0x100000000  # EPD

    player1 &= 0xFFFFFFFF
    player2 &= 0xFFFFFFFF

    return pack(
        "<IIIIIIHBBBBH",
        locid1,
        strid,
        wavid,
        time,
        player1,
        player2,
        unitid,
        acttype,
        amount,
        flags,
        0,
        eudx,
    )


def Trigger(  # noqa: N802
    players: list[Player],
    conditions: list[bytes] | bytes = [],
    actions: list[bytes] | bytes = [],
) -> bytes:
    conditions = FlattenList(conditions)
    actions = FlattenList(actions)

    ep_assert(isinstance(players, list), f"players is not list: {players}")
    ep_assert(isinstance(conditions, list), f"conditions is not list: {conditions}")
    ep_assert(isinstance(actions, list), f"actions is not list: {actions}")
    ep_assert(len(conditions) <= 16, f"16 < len(conditions): {len(conditions)}")
    ep_assert(len(actions) <= 64, f"64 < len(actions): {len(actions)}")
    peff = bytearray(28)
    for p in players:
        peff[EncodePlayer(p)] = 1

    b = b"".join(
        [
            *conditions,
            bytes(20 * (16 - len(conditions))),
            *actions,
            bytes(32 * (64 - len(actions))),
            b"\x04\0\0\0",
            bytes(peff),
        ]
    )
    ep_assert(len(b) == 2400, f"len(trigger) != 2400: {len(b)}")
    return b


# predefined conditions
def NoCondition() -> bytes:  # noqa: N802
    return Condition(0, 0, 0, 0, 0, 0, 0, 0)


def CountdownTimer(comparison: Comparison, time: int) -> bytes:  # noqa: N802
    comparison = EncodeComparison(comparison)
    return Condition(0, 0, time, 0, comparison, 1, 0, 0)


def Command(  # noqa: N802
    player: Player, comparison: Comparison, number: int, unit: Unit
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 2, 0, 0)


def Bring(  # noqa: N802
    player: Player,
    comparison: Comparison,
    number: int,
    unit: Unit,
    location: Location,
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, player, number, unit, comparison, 3, 0, 0)


def Accumulate(  # noqa: N802
    player: Player,
    comparison: Comparison,
    number: int,
    resource_type: Resource,
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    resource_type = EncodeResource(resource_type)
    return Condition(0, player, number, 0, comparison, 4, resource_type, 0)


def __kills__internal(
    player: Player, comparison: Comparison, number: int, unit: Unit
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 5, 0, 0)


Kills = _Kills()
Kills._internalf = __kills__internal


def CommandMost(unit: Unit) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 6, 0, 0)


def CommandMostAt(unit: Unit, location: Location) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, 0, 0, unit, 0, 7, 0, 0)


def MostKills(unit: Unit) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 8, 0, 0)


def HighestScore(score_type: _Score) -> bytes:  # noqa: N802
    score_type = EncodeScore(score_type)
    return Condition(0, 0, 0, 0, 0, 9, score_type, 0)


def MostResources(resource_type: Resource) -> bytes:  # noqa: N802
    resource_type = EncodeResource(resource_type)
    return Condition(0, 0, 0, 0, 0, 10, resource_type, 0)


def Switch(switch: _Switch, state: SwitchState) -> bytes:  # noqa: N802
    switch = EncodeSwitch(switch)
    state = EncodeSwitchState(state)
    return Condition(0, 0, 0, 0, state, 11, switch, 0)


def ElapsedTime(comparison: Comparison, time: int) -> bytes:  # noqa: N802
    comparison = EncodeComparison(comparison)
    return Condition(0, 0, time, 0, comparison, 12, 0, 0)


def Briefing() -> bytes:  # noqa: N802
    return Condition(0, 0, 0, 0, 0, 13, 0, 0)


def Opponents(player: Player, comparison: Comparison, number: int) -> bytes:  # noqa: N802
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    return Condition(0, player, number, 0, comparison, 14, 0, 0)


def Deaths(  # noqa: N802
    player: Player, comparison: Comparison, number: int, unit: Unit
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(0, player, number, unit, comparison, 15, 0, 0)


def CommandLeast(unit: Unit) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 16, 0, 0)


def CommandLeastAt(unit: Unit, location: Location) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    return Condition(location, 0, 0, unit, 0, 17, 0, 0)


def LeastKills(unit: Unit) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    return Condition(0, 0, 0, unit, 0, 18, 0, 0)


def LowestScore(score_type: _Score) -> bytes:  # noqa: N802
    score_type = EncodeScore(score_type)
    return Condition(0, 0, 0, 0, 0, 19, score_type, 0)


def LeastResources(resource_type: Resource) -> bytes:  # noqa: N802
    resource_type = EncodeResource(resource_type)
    return Condition(0, 0, 0, 0, 0, 20, resource_type, 0)


def Score(  # noqa: N802
    player: Player, score_type: _Score, comparison: Comparison, number: int
) -> bytes:
    player = EncodePlayer(player)
    score_type = EncodeScore(score_type)
    comparison = EncodeComparison(comparison)
    return Condition(0, player, number, 0, comparison, 21, score_type, 0)


def Always() -> bytes:  # noqa: N802
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never() -> bytes:  # noqa: N802
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


# predefined Action
def NoAction() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 0, 0, 4)


def Victory() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(time: int) -> bytes:  # noqa: N802
    return Action(0, 0, 0, time, 0, 0, 0, 4, 0, 4)


def PauseGame() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(  # noqa: N802
    unit: Unit,
    where: Location,
    sound_name: String,
    time_modifier: Modifier,
    time: int,
    text: String,
    AlwaysDisplay: int = 4,  # noqa: N803
) -> bytes:
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    sound_name = EncodeString(sound_name)
    modifier = EncodeModifier(time_modifier)
    text = EncodeString(text)
    return Action(where, text, sound_name, time, 0, 0, unit, 7, modifier, 4)


def PlayWAV(sound_name: String) -> bytes:  # noqa: N802
    sound_name = EncodeString(sound_name)
    return Action(0, 0, sound_name, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(text: String, AlwaysDisplay: int = 4) -> bytes:  # noqa: N802, N803
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 9, 0, 4)


def CenterView(where: Location) -> bytes:  # noqa: N802
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(  # noqa: N802
    count: int,
    unit: Unit,
    where: Location,
    player: Player,
    properties: UnitProperty | bytes,
) -> bytes:
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    player = EncodePlayer(player)
    prop = EncodeProperty(properties)
    return Action(where, 0, 0, 0, player, prop, unit, 11, count, 28)


def SetMissionObjectives(text: String) -> bytes:  # noqa: N802
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(switch: _Switch, state: SwitchAction) -> bytes:  # noqa: N802
    switch = EncodeSwitch(switch)
    state = EncodeSwitchAction(state)
    return Action(0, 0, 0, 0, 0, switch, 0, 13, state, 4)


def SetCountdownTimer(time_modifier: Modifier, time: int) -> bytes:  # noqa: N802
    modifier = EncodeModifier(time_modifier)
    return Action(0, 0, 0, time, 0, 0, 0, 14, modifier, 4)


def RunAIScript(script: AIScript) -> bytes:  # noqa: N802
    script = EncodeAIScript(script)
    return Action(0, 0, 0, 0, 0, script, 0, 15, 0, 4)


def RunAIScriptAt(script: AIScript, where: Location) -> bytes:  # noqa: N802
    script = EncodeAIScript(script)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, script, 0, 16, 0, 4)


def LeaderBoardControl(unit: Unit, label: String) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, unit, 17, 0, 20)


def LeaderBoardControlAt(  # noqa: N802
    unit: Unit, location: Location, label: String
) -> bytes:
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    label = EncodeString(label)
    return Action(location, label, 0, 0, 0, 0, unit, 18, 0, 20)


def LeaderBoardResources(resource_type: Resource, label: String) -> bytes:  # noqa: N802
    resource_type = EncodeResource(resource_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, resource_type, 19, 0, 4)


def LeaderBoardKills(unit: Unit, label: String) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, unit, 20, 0, 20)


def LeaderBoardScore(score_type: _Score, label: String) -> bytes:  # noqa: N802
    score_type = EncodeScore(score_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, score_type, 21, 0, 4)


def KillUnit(unit: Unit, player: Player) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    player = EncodePlayer(player)
    return Action(0, 0, 0, 0, player, 0, unit, 22, 0, 20)


def KillUnitAt(  # noqa: N802
    count: Count, unit: Unit, where: Location, for_player: Player
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 23, count, 20)


def RemoveUnit(unit: Unit, player: Player) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    player = EncodePlayer(player)
    return Action(0, 0, 0, 0, player, 0, unit, 24, 0, 20)


def RemoveUnitAt(  # noqa: N802
    count: Count, unit: Unit, where: Location, for_player: Player
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 25, count, 20)


def SetResources(  # noqa: N802
    player: Player, modifier: Modifier, amount: int, resource_type: Resource
) -> bytes:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    resource_type = EncodeResource(resource_type)
    return Action(0, 0, 0, 0, player, amount, resource_type, 26, modifier, 4)


def SetScore(  # noqa: N802
    player: Player, modifier: Modifier, amount: int, score_type: _Score
) -> bytes:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    score_type = EncodeScore(score_type)
    return Action(0, 0, 0, 0, player, amount, score_type, 27, modifier, 4)


def MinimapPing(where: Location) -> bytes:  # noqa: N802
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(unit: Unit, time: int) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    return Action(0, 0, 0, time, 0, 0, unit, 29, 0, 20)


def MuteUnitSpeech() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(state: PropState) -> bytes:  # noqa: N802
    state = EncodePropState(state)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, state, 4)


def LeaderBoardGoalControl(goal: int, unit: Unit, label: String) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, unit, 33, 0, 20)


def LeaderBoardGoalControlAt(  # noqa: N802
    goal: int, unit: Unit, location: Location, label: String
) -> bytes:
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    label = EncodeString(label)
    return Action(location, label, 0, 0, 0, goal, unit, 34, 0, 20)


def LeaderBoardGoalResources(  # noqa: N802
    goal: int, resource_type: Resource, label: String
) -> bytes:
    resource_type = EncodeResource(resource_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, resource_type, 35, 0, 4)


def LeaderBoardGoalKills(goal: int, unit: Unit, label: String) -> bytes:  # noqa: N802
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, unit, 36, 0, 20)


def LeaderBoardGoalScore(  # noqa: N802
    goal: int, score_type: _Score, label: String
) -> bytes:
    score_type = EncodeScore(score_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, score_type, 37, 0, 4)


def MoveLocation(  # noqa: N802
    location: Location, on_unit: Unit, owner: Player, dest_location: Location
) -> bytes:
    location = EncodeLocation(location)
    on_unit = EncodeUnit(on_unit)
    owner = EncodePlayer(owner)
    dest_location = EncodeLocation(dest_location)
    return Action(dest_location, 0, 0, 0, owner, location, on_unit, 38, 0, 20)


def MoveUnit(  # noqa: N802
    count: Count,
    unit_type: Unit,
    owner: Player,
    start_location: Location,
    dest_location: Location,
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit_type)
    owner = EncodePlayer(owner)
    startloc = EncodeLocation(start_location)
    dest_location = EncodeLocation(dest_location)
    return Action(startloc, 0, 0, 0, owner, dest_location, unit, 39, count, 20)


def LeaderBoardGreed(goal: int) -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, goal, 0, 40, 0, 4)


def SetNextScenario(scenario_name: String) -> bytes:  # noqa: N802
    scenario_name = EncodeString(scenario_name)
    return Action(0, scenario_name, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(  # noqa: N802
    state: PropState, unit: Unit, owner: Player, where: Location
) -> bytes:
    state = EncodePropState(state)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, 0, unit, 42, state, 20)


def SetInvincibility(  # noqa: N802
    state: PropState, unit: Unit, owner: Player, where: Location
) -> bytes:
    state = EncodePropState(state)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, 0, unit, 43, state, 20)


def CreateUnit(  # noqa: N802
    number: int, unit: Unit, where: Location, for_player: Player
) -> bytes:
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 44, number, 20)


def SetDeaths(  # noqa: N802
    player: Player, modifier: Modifier, number: int, unit: Unit
) -> bytes:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    unit = EncodeUnit(unit)
    return Action(0, 0, 0, 0, player, number, unit, 45, modifier, 20)


def Order(  # noqa: N802
    unit: Unit,
    owner: Player,
    start_location: Location,
    order_type: _Order,
    dest_location: Location,
) -> bytes:
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    startloc = EncodeLocation(start_location)
    order_type = EncodeOrder(order_type)
    dest_location = EncodeLocation(dest_location)
    return Action(startloc, 0, 0, 0, owner, dest_location, unit, 46, order_type, 20)


def Comment(text: String) -> bytes:  # noqa: N802
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, new_owner: Player
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    new_owner = EncodePlayer(new_owner)
    return Action(where, 0, 0, 0, owner, new_owner, unit, 48, count, 20)


def ModifyUnitHitPoints(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: int
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 49, count, 20)


def ModifyUnitEnergy(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: int
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 50, count, 20)


def ModifyUnitShields(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: int
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 51, count, 20)


def ModifyUnitResourceAmount(  # noqa: N802
    count: Count, owner: Player, where: Location, new_value: int
) -> bytes:
    count = EncodeCount(count)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, new_value, 0, 52, count, 4)


def ModifyUnitHangarCount(  # noqa: N802
    add: int, count: Count, unit: Unit, owner: Player, where: Location
) -> bytes:
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, add, unit, 53, count, 20)


def PauseTimer() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw() -> bytes:  # noqa: N802
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(player: Player, status: AllyStatus) -> bytes:  # noqa: N802
    player = EncodePlayer(player)
    status = EncodeAllyStatus(status)
    return Action(0, 0, 0, 0, player, 0, status, 57, 0, 4)


# compound triggers
def Memory(dest: int, cmptype: Comparison, value: int) -> bytes:  # noqa: N802
    return Deaths(EPD(dest), cmptype, value, 0)


def SetMemory(dest: int, modtype, value: int) -> bytes:  # noqa: N802
    return SetDeaths(EPD(dest), modtype, value, 0)


def DeathsX(  # noqa: N802
    player: Player, comparison: Comparison, number: int, unit: Unit, mask: int
) -> bytes:
    player = EncodePlayer(player)
    comparison = EncodeComparison(comparison)
    unit = EncodeUnit(unit)
    return Condition(mask, player, number, unit, comparison, 15, 0, 0, eudx=0x4353)


def MemoryX(dest: int, cmptype: Comparison, value: int, mask: int) -> bytes:  # noqa: N802
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def SetDeathsX(  # noqa: N802
    player: Player, modifier: Modifier, number: int, unit: Unit, mask: int
) -> bytes:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    unit = EncodeUnit(unit)
    return Action(mask, 0, 0, 0, player, number, unit, 45, modifier, 20, eudx=0x4353)


def SetMemoryX(dest: int, modtype: Modifier, value: int, mask: int) -> bytes:  # noqa: N802
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)
