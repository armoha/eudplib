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

from struct import pack

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
    _KillsSpecialized,
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


def Condition(
    locid, player, amount, unitid, comparison, condtype, restype, flag, *, eudx=0
) -> bytes:
    if player < 0:
        player += 0x100000000  # EPD

    player &= 0xFFFFFFFF
    amount &= 0xFFFFFFFF
    if isinstance(eudx, str):
        eudx = b2i2(u2b(eudx))

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
    locid1, strid, wavid, time, player1, player2, unitid, acttype, amount, flags, *, eudx=0
) -> bytes:
    player1 &= 0xFFFFFFFF
    player2 &= 0xFFFFFFFF

    if player1 < 0:
        player1 += 0x100000000  # EPD
    if player2 < 0:
        player2 += 0x100000000  # EPD
    if isinstance(eudx, str):
        eudx = b2i2(u2b(eudx))
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
    players: list, conditions: list[bytes] | bytes = [], actions: list[bytes] | bytes = []
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


def CountdownTimer(Comparison, Time: int) -> bytes:
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)


def Command(Player, Comparison, Number: int, Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)


def Bring(Player, Comparison, Number: int, Unit, Location) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)


def Accumulate(Player, Comparison, Number: int, ResourceType) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)


def __Kills__internal(Player, Comparison, Number: int, Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)


Kills = _KillsSpecialized("Kiils")
Kills._internalf = __Kills__internal


def CommandMost(Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)


def CommandMostAt(Unit, Location) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)


def MostKills(Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)


def HighestScore(ScoreType) -> bytes:
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 9, ScoreType, 0)


def MostResources(ResourceType) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)


def Switch(Switch, State) -> bytes:
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchState(State)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)


def ElapsedTime(Comparison, Time: int) -> bytes:
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)


def Briefing() -> bytes:
    return Condition(0, 0, 0, 0, 0, 13, 0, 0)


def Opponents(Player, Comparison, Number: int) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)


def Deaths(Player, Comparison, Number: int, Unit) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)


def CommandLeast(Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)


def CommandLeastAt(Unit, Location) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)


def LeastKills(Unit) -> bytes:
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)


def LowestScore(ScoreType) -> bytes:
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 19, ScoreType, 0)


def LeastResources(ResourceType) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)


def Score(Player, ScoreType, Comparison, Number: int) -> bytes:
    Player = EncodePlayer(Player)
    ScoreType = EncodeScore(ScoreType)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 21, ScoreType, 0)


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


def Wait(Time) -> bytes:
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(
    Unit, Where, WAVName, TimeModifier, Time: int, Text, AlwaysDisplay: int = 4
) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    WAVName = EncodeString(WAVName)
    TimeModifier = EncodeModifier(TimeModifier)
    Text = EncodeString(Text)
    return Action(Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, AlwaysDisplay)


def PlayWAV(WAVName) -> bytes:
    WAVName = EncodeString(WAVName)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text, AlwaysDisplay: int = 4) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, AlwaysDisplay)


def CenterView(Where) -> bytes:
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(Count: int, Unit, Where, Player, Properties) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    Player = EncodePlayer(Player)
    Properties = EncodeProperty(Properties)
    return Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch, State) -> bytes:
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchAction(State)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier, Time: int) -> bytes:
    TimeModifier = EncodeModifier(TimeModifier)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script) -> bytes:
    Script = EncodeAIScript(Script)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script, Where) -> bytes:
    Script = EncodeAIScript(Script)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit, Location, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType, Label) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(ScoreType, Label) -> bytes:
    ScoreType = EncodeScore(ScoreType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Score, 21, 0, 4)


def KillUnit(Unit, Player) -> bytes:
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count, Unit, Where, ForPlayer) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit, Player) -> bytes:
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count, Unit, Where, ForPlayer) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player, Modifier, Amount: int, ResourceType) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    ResourceType = EncodeResource(ResourceType)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player, Modifier, Amount: int, ScoreType) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    ScoreType = EncodeScore(ScoreType)
    return Action(0, 0, 0, 0, Player, Amount, ScoreType, 27, Modifier, 4)


def MinimapPing(Where) -> bytes:
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit, Time) -> bytes:
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech() -> bytes:
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State) -> bytes:
    State = EncodePropState(State)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal: int, Unit, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal: int, Unit, Location, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal: int, ResourceType, Label) -> bytes:
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal: int, Unit, Label) -> bytes:
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal: int, ScoreType, Label) -> bytes:
    ScoreType = EncodeScore(ScoreType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, ScoreType, 37, 0, 4)


def MoveLocation(Location, OnUnit, Owner, DestLocation) -> bytes:
    Location = EncodeLocation(Location)
    OnUnit = EncodeUnit(OnUnit)
    Owner = EncodePlayer(Owner)
    DestLocation = EncodeLocation(DestLocation)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation) -> bytes:
    Count = EncodeCount(Count)
    UnitType = EncodeUnit(UnitType)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal) -> bytes:
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName) -> bytes:
    ScenarioName = EncodeString(ScenarioName)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State, Unit, Owner, Where) -> bytes:
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State, Unit, Owner, Where) -> bytes:
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number: int, Unit, Where, ForPlayer) -> bytes:
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player, Modifier, Number: int, Unit) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(Unit, Owner, StartLocation, OrderType, DestLocation) -> bytes:
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    OrderType = EncodeOrder(OrderType)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, OrderType, 20)


def Comment(Text) -> bytes:
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count, Unit, Owner, Where, NewOwner) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    NewOwner = EncodePlayer(NewOwner)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent: int) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(Count, Unit, Owner, Where, Percent: int) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(Count, Unit, Owner, Where, Percent: int) -> bytes:
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count, Owner, Where, NewValue: int) -> bytes:
    Count = EncodeCount(Count)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(Add: int, Count, Unit, Owner, Where) -> bytes:
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


def SetAllianceStatus(Player, Status) -> bytes:
    Player = EncodePlayer(Player)
    Status = EncodeAllyStatus(Status)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)


# compound triggers
def Memory(dest: int, cmptype, value: int) -> bytes:
    return Deaths(EPD(dest), cmptype, value, 0)


def SetMemory(dest: int, modtype, value: int) -> bytes:
    return SetDeaths(EPD(dest), modtype, value, 0)


def DeathsX(Player, Comparison, Number: int, Unit, Mask: int) -> bytes:
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx="SC")


def MemoryX(dest: int, cmptype, value: int, mask: int) -> bytes:
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def SetDeathsX(Player, Modifier, Number: int, Unit, Mask: int) -> bytes:
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx="SC")


def SetMemoryX(dest: int, modtype, value: int, mask: int) -> bytes:
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)
