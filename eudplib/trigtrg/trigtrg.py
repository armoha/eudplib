#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from struct import pack
from typing import TypeAlias

from ..core import UnitProperty
from ..core.rawtrigger.constenc import (
    P1,
    P2,
    P3,
    P4,
    P5,
    P6,
    P7,
    P8,
    P9,
    P10,
    P11,
    P12,
    Add,
    All,
    AlliedVictory,
    Allies,
    AllPlayers,
    Ally,
    AtLeast,
    AtMost,
    Attack,
    Buildings,
    Clear,
    Cleared,
    CurrentPlayer,
    Custom,
    Disable,
    Enable,
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
    Enemy,
    Exactly,
    Foes,
    Force1,
    Force2,
    Force3,
    Force4,
    Gas,
    KillsAndRazings,
    Move,
    NeutralPlayers,
    NonAlliedVictoryPlayers,
    Ore,
    OreAndGas,
    Patrol,
    Player1,
    Player2,
    Player3,
    Player4,
    Player5,
    Player6,
    Player7,
    Player8,
    Player9,
    Player10,
    Player11,
    Player12,
    Random,
    Razings,
    Set,
    SetTo,
    Subtract,
    Toggle,
    Total,
    Units,
    UnitsAndBuildings,
    TrgAllyStatus,
    TrgComparison,
    TrgCount,
    _KillsSpecialized,
    TrgModifier,
    TrgPlayer,
    TrgPropState,
    TrgResource,
    TrgOrder,
    TrgScore,
    TrgSwitchAction,
    TrgSwitchState,
)
from ..core.rawtrigger.strenc import (
    EncodeAIScript,
    EncodeLocation,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
)
from ..localize import _
from ..utils import EPD, FlattenList, b2i2, ep_assert, u2b, unProxy

"""
Defines stock conditions & actions. You are most likely to use only conditions
declared in this file. This file also serves as a basic reference for trigger
condition / actions.

 ex) You want to create 'Create Unit' action:
   1. Remove spaces. 'CreateUnit'
   2. Find 'CreateUnit' in this file. You'll see the following function def.
     def CreateUnit(Number, Unit, Where, ForPlayer):
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


def Condition(
    locid: int,
    player: int,
    amount: int,
    unitid: int,
    comparison: int,
    condtype: int,
    restype: int,
    flag: int,
    *,
    eudx: int = 0
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


def Action(
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
    eudx: int = 0
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


def Trigger(
    players: list[Player],
    conditions: list[bytes] | bytes = [],
    actions: list[bytes] | bytes = [],
) -> bytes:
    conditions = FlattenList(conditions)
    actions = FlattenList(actions)

    ep_assert(type(players) is list)
    ep_assert(type(conditions) is list)
    ep_assert(type(actions) is list)
    ep_assert(len(conditions) <= 16)
    ep_assert(len(actions) <= 64)
    peff = bytearray(28)
    for p in players:
        peff[EncodePlayer(p)] = 1

    b = b"".join(
        conditions
        + [bytes(20 * (16 - len(conditions)))]
        + actions
        + [bytes(32 * (64 - len(actions)))]
        + [b"\x04\0\0\0"]
        + [bytes(peff)]
    )
    ep_assert(len(b) == 2400)
    return b


# predefined conditions
def NoCondition() -> bytes:
    return Condition(0, 0, 0, 0, 0, 0, 0, 0)


def CountdownTimer(Comparison: Comparison, Time: int) -> bytes:
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)


def Command(Player: Player, Comparison: Comparison, Number: int, Unit: Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)


def Bring(
    Player: Player, Comparison: Comparison, Number: int, Unit: Unit, Location: Location
) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)


def Accumulate(
    Player: Player, Comparison: Comparison, Number: int, ResourceType: Resource
) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)


def __Kills__internal(Player: Player, Comparison: Comparison, Number: int, Unit: Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)


Kills = _KillsSpecialized("Kills")
Kills._internalf = __Kills__internal


def CommandMost(Unit: Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)


def CommandMostAt(Unit: Unit, Location: Location) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)


def MostKills(Unit: Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)


def HighestScore(TrgScore: _Score) -> bytes:
    TrgScore = EncodeScore(TrgScore)
    return Condition(0, 0, 0, 0, 0, 9, TrgScore, 0)


def MostResources(ResourceType: Resource) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)


def Switch(Switch: _Switch, State: SwitchState) -> bytes:
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchState(State)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)


def ElapsedTime(Comparison: Comparison, Time: int) -> bytes:
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)


def Briefing() -> bytes:
    return Condition(0, 0, 0, 0, 0, 13, 0, 0)


def Opponents(Player: Player, Comparison: Comparison, Number: int) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)


def Deaths(Player: Player, Comparison: Comparison, Number: int, Unit: Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)


def CommandLeast(Unit: Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)


def CommandLeastAt(Unit: Unit, Location: Location) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)


def LeastKills(Unit: Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)


def LowestScore(TrgScore: _Score) -> bytes:
    TrgScore = EncodeScore(TrgScore)
    return Condition(0, 0, 0, 0, 0, 19, TrgScore, 0)


def LeastResources(ResourceType: Resource) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)


def Score(Player: Player, TrgScore: _Score, Comparison: Comparison, Number: int) -> bytes:
    Player = EncodePlayer(Player)
    TrgScore = EncodeScore(TrgScore)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 21, TrgScore, 0)


def Always() -> bytes:
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never() -> bytes:
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


# predefined Action
def NoAction() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 0, 0, 4)


def Victory() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(Time: int) -> bytes:
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(
    Unit: Unit,
    Where: Location,
    WAVName: String,
    TimeModifier: Modifier,
    Time: int,
    Text: String,
    AlwaysDisplay: int = 4,
) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    WAVName = EncodeString(WAVName)
    TimeModifier = EncodeModifier(TimeModifier)
    Text = EncodeString(Text)
    return Action(Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, 4)


def PlayWAV(WAVName: String) -> bytes:
    WAVName = EncodeString(WAVName)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text: String, AlwaysDisplay: int = 4) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, 4)


def CenterView(Where: Location) -> bytes:
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(
    Count: int, Unit: Unit, Where: Location, Player: Player, Properties: UnitProperty | bytes
) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    Player = EncodePlayer(Player)
    properties = EncodeProperty(Properties)
    return Action(Where, 0, 0, 0, Player, properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text: String) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch: _Switch, State: SwitchAction) -> bytes:
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchAction(State)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier: Modifier, Time: int) -> bytes:
    TimeModifier = EncodeModifier(TimeModifier)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script: AIScript) -> bytes:
    Script = EncodeAIScript(Script)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script: AIScript, Where: Location) -> bytes:
    Script = EncodeAIScript(Script)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit: Unit, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit: Unit, Location: Location, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType: Resource, Label: String) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit: Unit, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(TrgScore: _Score, Label: String) -> bytes:
    TrgScore = EncodeScore(TrgScore)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, TrgScore, 21, 0, 4)


def KillUnit(Unit: Unit, Player: Player) -> bytes:
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count: Count, Unit: Unit, Where: Location, ForPlayer: Player) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit: Unit, Player: Player) -> bytes:
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count: Count, Unit: Unit, Where: Location, ForPlayer: Player) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player: Player, Modifier: Modifier, Amount: int, ResourceType: Resource) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    ResourceType = EncodeResource(ResourceType)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player: Player, Modifier: Modifier, Amount: int, TrgScore: _Score) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    TrgScore = EncodeScore(TrgScore)
    return Action(0, 0, 0, 0, Player, Amount, TrgScore, 27, Modifier, 4)


def MinimapPing(Where: Location) -> bytes:
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit: Unit, Time: int) -> bytes:
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State: PropState) -> bytes:
    State = EncodePropState(State)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal: int, Unit: Unit, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal: int, Unit: Unit, Location: Location, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal: int, ResourceType: Resource, Label: String) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal: int, Unit: Unit, Label: String) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal: int, TrgScore: _Score, Label: String) -> bytes:
    TrgScore = EncodeScore(TrgScore)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, TrgScore, 37, 0, 4)


def MoveLocation(Location: Location, OnUnit: Unit, Owner: Player, DestLocation: Location) -> bytes:
    Location = EncodeLocation(Location)
    OnUnit = EncodeUnit(OnUnit)
    Owner = EncodePlayer(Owner)
    DestLocation = EncodeLocation(DestLocation)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(
    Count: Count, UnitType: Unit, Owner: Player, StartLocation: Location, DestLocation: Location
) -> bytes:
    Count = EncodeCount(Count)
    UnitType = EncodeUnit(UnitType)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal: int) -> bytes:
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName: String) -> bytes:
    ScenarioName = EncodeString(ScenarioName)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State: PropState, Unit: Unit, Owner: Player, Where: Location) -> bytes:
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State: PropState, Unit: Unit, Owner: Player, Where: Location) -> bytes:
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number: int, Unit: Unit, Where: Location, ForPlayer: Player) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player: Player, Modifier: Modifier, Number: int, Unit: Unit) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(
    Unit: Unit, Owner: Player, StartLocation: Location, TrgOrder: _Order, DestLocation: Location
) -> bytes:
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    TrgOrder = EncodeOrder(TrgOrder)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, TrgOrder, 20)


def Comment(Text: String) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count: Count, Unit: Unit, Owner: Player, Where: Location, NewOwner: Player) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    NewOwner = EncodePlayer(NewOwner)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(
    Count: Count, Unit: Unit, Owner: Player, Where: Location, Percent: int
) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(
    Count: Count, Unit: Unit, Owner: Player, Where: Location, Percent: int
) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(
    Count: Count, Unit: Unit, Owner: Player, Where: Location, Percent: int
) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count: Count, Owner: Player, Where: Location, NewValue: int) -> bytes:
    Count = EncodeCount(Count)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(
    Add: int, Count: Count, Unit: Unit, Owner: Player, Where: Location
) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Add, Unit, 53, Count, 20)


def PauseTimer() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(Player: Player, Status: AllyStatus) -> bytes:
    Player = EncodePlayer(Player)
    Status = EncodeAllyStatus(Status)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)


# compound triggers
def Memory(dest: int, cmptype: Comparison, value: int) -> bytes:
    return Deaths(EPD(dest), cmptype, value, 0)


def SetMemory(dest: int, modtype, value: int) -> bytes:
    return SetDeaths(EPD(dest), modtype, value, 0)


def DeathsX(Player: Player, Comparison: Comparison, Number: int, Unit: Unit, Mask: int) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx=0x4353)


def MemoryX(dest: int, cmptype: Comparison, value: int, mask: int) -> bytes:
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def SetDeathsX(Player: Player, Modifier: Modifier, Number: int, Unit: Unit, Mask: int) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx=0x4353)


def SetMemoryX(dest: int, modtype: Modifier, value: int, mask: int) -> bytes:
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)
