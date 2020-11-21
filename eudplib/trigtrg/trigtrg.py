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
from eudplib import utils as ut
from ..localize import _
from ..utils import EPD, b2i2, u2b, ep_assert
from ..core.rawtrigger.constenc import *
from ..core.rawtrigger.strenc import *

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
):
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
    *,
    eudx=0
):
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


def Trigger(players, conditions=[], actions=[]):
    conditions = ut.FlattenList(conditions)
    actions = ut.FlattenList(actions)

    ut.ep_assert(type(players) is list)
    ut.ep_assert(type(conditions) is list)
    ut.ep_assert(type(actions) is list)
    ut.ep_assert(len(conditions) <= 16)
    ut.ep_assert(len(actions) <= 64)
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
    ut.ep_assert(len(b) == 2400)
    return b


# predefined conditions
def NoCondition():
    return Condition(0, 0, 0, 0, 0, 0, 0, 0)


def CountdownTimer(Comparison, Time):
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 1, 0, 0)


def Command(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 2, 0, 0)


def Bring(Player, Comparison, Number, Unit, Location):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, Player, Number, Unit, Comparison, 3, 0, 0)


def Accumulate(Player, Comparison, Number, ResourceType):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, Player, Number, 0, Comparison, 4, ResourceType, 0)


def Kills(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 5, 0, 0)


def CommandMost(Unit):
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 6, 0, 0)


def CommandMostAt(Unit, Location):
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 7, 0, 0)


def MostKills(Unit):
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 8, 0, 0)


def HighestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 9, ScoreType, 0)


def MostResources(ResourceType):
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 10, ResourceType, 0)


def Switch(Switch, State):
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchState(State)
    return Condition(0, 0, 0, 0, State, 11, Switch, 0)


def ElapsedTime(Comparison, Time):
    Comparison = EncodeComparison(Comparison)
    return Condition(0, 0, Time, 0, Comparison, 12, 0, 0)


def Briefing():
    return Condition(0, 0, 0, 0, 0, 13, 0, 0)


def Opponents(Player, Comparison, Number):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 14, 0, 0)


def Deaths(Player, Comparison, Number, Unit):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(0, Player, Number, Unit, Comparison, 15, 0, 0)


def CommandLeast(Unit):
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 16, 0, 0)


def CommandLeastAt(Unit, Location):
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    return Condition(Location, 0, 0, Unit, 0, 17, 0, 0)


def LeastKills(Unit):
    Unit = EncodeUnit(Unit)
    return Condition(0, 0, 0, Unit, 0, 18, 0, 0)


def LowestScore(ScoreType):
    ScoreType = EncodeScore(ScoreType)
    return Condition(0, 0, 0, 0, 0, 19, ScoreType, 0)


def LeastResources(ResourceType):
    ResourceType = EncodeResource(ResourceType)
    return Condition(0, 0, 0, 0, 0, 20, ResourceType, 0)


def Score(Player, ScoreType, Comparison, Number):
    Player = EncodePlayer(Player)
    ScoreType = EncodeScore(ScoreType)
    Comparison = EncodeComparison(Comparison)
    return Condition(0, Player, Number, 0, Comparison, 21, ScoreType, 0)


def Always():
    return Condition(0, 0, 0, 0, 0, 22, 0, 0)


def Never():
    return Condition(0, 0, 0, 0, 0, 23, 0, 0)


# predefined Action
def NoAction():
    return Action(0, 0, 0, 0, 0, 0, 0, 0, 0, 4)


def Victory():
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat():
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger():
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(Time):
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(Unit, Where, WAVName, TimeModifier, Time, Text, AlwaysDisplay=4):
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    WAVName = EncodeString(WAVName)
    TimeModifier = EncodeModifier(TimeModifier)
    Text = EncodeString(Text)
    return Action(
        Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, AlwaysDisplay
    )


def PlayWAV(WAVName):
    WAVName = EncodeString(WAVName)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text, AlwaysDisplay=4):
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, AlwaysDisplay)


def CenterView(Where):
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(Count, Unit, Where, Player, Properties):
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    Player = EncodePlayer(Player)
    Properties = EncodeProperty(Properties)
    return Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text):
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch, State):
    Switch = EncodeSwitch(Switch)
    State = EncodeSwitchAction(State)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier, Time):
    TimeModifier = EncodeModifier(TimeModifier)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script):
    Script = EncodeAIScript(Script)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script, Where):
    Script = EncodeAIScript(Script)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit, Label):
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit, Location, Label):
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType, Label):
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit, Label):
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(ScoreType, Label):
    ScoreType = EncodeScore(ScoreType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, 0, Score, 21, 0, 4)


def KillUnit(Unit, Player):
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit, Player):
    Unit = EncodeUnit(Unit)
    Player = EncodePlayer(Player)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player, Modifier, Amount, ResourceType):
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    ResourceType = EncodeResource(ResourceType)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player, Modifier, Amount, ScoreType):
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    ScoreType = EncodeScore(ScoreType)
    return Action(0, 0, 0, 0, Player, Amount, ScoreType, 27, Modifier, 4)


def MinimapPing(Where):
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit, Time):
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State):
    State = EncodePropState(State)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal, Unit, Label):
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal, Unit, Location, Label):
    Unit = EncodeUnit(Unit)
    Location = EncodeLocation(Location)
    Label = EncodeString(Label)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal, ResourceType, Label):
    ResourceType = EncodeResource(ResourceType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal, Unit, Label):
    Unit = EncodeUnit(Unit)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal, ScoreType, Label):
    ScoreType = EncodeScore(ScoreType)
    Label = EncodeString(Label)
    return Action(0, Label, 0, 0, 0, Goal, ScoreType, 37, 0, 4)


def MoveLocation(Location, OnUnit, Owner, DestLocation):
    Location = EncodeLocation(Location)
    OnUnit = EncodeUnit(OnUnit)
    Owner = EncodePlayer(Owner)
    DestLocation = EncodeLocation(DestLocation)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation):
    Count = EncodeCount(Count)
    UnitType = EncodeUnit(UnitType)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal):
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName):
    ScenarioName = EncodeString(ScenarioName)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State, Unit, Owner, Where):
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State, Unit, Owner, Where):
    State = EncodePropState(State)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number, Unit, Where, ForPlayer):
    Unit = EncodeUnit(Unit)
    Where = EncodeLocation(Where)
    ForPlayer = EncodePlayer(ForPlayer)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player, Modifier, Number, Unit):
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(Unit, Owner, StartLocation, OrderType, DestLocation):
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    StartLocation = EncodeLocation(StartLocation)
    OrderType = EncodeOrder(OrderType)
    DestLocation = EncodeLocation(DestLocation)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, OrderType, 20)


def Comment(Text):
    Text = EncodeString(Text)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count, Unit, Owner, Where, NewOwner):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    NewOwner = EncodePlayer(NewOwner)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count, Owner, Where, NewValue):
    Count = EncodeCount(Count)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(Add, Count, Unit, Owner, Where):
    Count = EncodeCount(Count)
    Unit = EncodeUnit(Unit)
    Owner = EncodePlayer(Owner)
    Where = EncodeLocation(Where)
    return Action(Where, 0, 0, 0, Owner, Add, Unit, 53, Count, 20)


def PauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw():
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(Player, Status):
    Player = EncodePlayer(Player)
    Status = EncodeAllyStatus(Status)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)


# compound triggers
def Memory(dest, cmptype, value):
    if isMemDestStrict and isinstance(dest, int):
        ep_assert(dest % 4 == 0, _("Address should be multiple of 4"))
    return Deaths(EPD(dest), cmptype, value, 0)


def SetMemory(dest, modtype, value):
    if isMemDestStrict and isinstance(dest, int):
        ep_assert(dest % 4 == 0, _("Address should be multiple of 4"))
    return SetDeaths(EPD(dest), modtype, value, 0)


def DeathsX(Player, Comparison, Number, Unit, Mask):
    Player = EncodePlayer(Player)
    Comparison = EncodeComparison(Comparison)
    Unit = EncodeUnit(Unit)
    return Condition(Mask, Player, Number, Unit, Comparison, 15, 0, 0, eudx="SC")


def MemoryX(dest, cmptype, value, mask):
    if isMemDestStrict and isinstance(dest, int):
        ep_assert(dest % 4 == 0, _("Address should be multiple of 4"))
    return DeathsX(EPD(dest), cmptype, value, 0, mask)


def SetDeathsX(Player, Modifier, Number, Unit, Mask):
    Player = EncodePlayer(Player)
    Modifier = EncodeModifier(Modifier)
    Unit = EncodeUnit(Unit)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx="SC")


def SetMemoryX(dest, modtype, value, mask):
    if isMemDestStrict and isinstance(dest, int):
        ep_assert(dest % 4 == 0, _("Address should be multiple of 4"))
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)
