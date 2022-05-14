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

from .action import Action
from .constenc import (
    Add,
    CurrentPlayer,
    EncodeAllyStatus,
    EncodeCount,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSwitchAction,
)
from .strenc import (
    EncodeAIScript,
    EncodeLocation,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
)
from ...localize import _
from ...utils import EPD, ep_warn, ep_assert, unProxy


def Victory():
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat():
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger():
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(Time):
    ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame():
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(Unit, Where, WAVName, TimeModifier, Time, Text, AlwaysDisplay=4):
    from ...epscript import IsSCDBMap

    if not IsSCDBMap:
        ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    WAVName = EncodeString(WAVName, issueError=True)
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    Text = EncodeString(Text, issueError=True)
    return Action(
        Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, AlwaysDisplay
    )


def PlayWAV(WAVName):
    WAVName = EncodeString(WAVName, issueError=True)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text, AlwaysDisplay=4):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, AlwaysDisplay)


def CenterView(Where):
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(Count, Unit, Where, Player, Properties):
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    Properties = EncodeProperty(Properties, issueError=True)
    return Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch, State):
    Switch = EncodeSwitch(Switch, issueError=True)
    State = EncodeSwitchAction(State, issueError=True)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier, Time):
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script):
    Script = EncodeAIScript(Script, issueError=True)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script, Where):
    Script = EncodeAIScript(Script, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit, Location, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType, Label):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(ScoreType, Label):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ScoreType, 21, 0, 4)


def KillUnit(Unit, Player):
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit, Player):
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count, Unit, Where, ForPlayer):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player, Modifier, Amount, ResourceType):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player, Modifier, Amount, ScoreType):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ScoreType, 27, Modifier, 4)


def MinimapPing(Where):
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit, Time):
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech():
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State):
    State = EncodePropState(State, issueError=True)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal, Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal, Unit, Location, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal, ResourceType, Label):
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal, Unit, Label):
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal, ScoreType, Label):
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ScoreType, 37, 0, 4)


def MoveLocation(Location, OnUnit, Owner, DestLocation):
    Location = EncodeLocation(Location, issueError=True)
    OnUnit = EncodeUnit(OnUnit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation):
    Count = EncodeCount(Count, issueError=True)
    UnitType = EncodeUnit(UnitType, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal):
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName):
    ScenarioName = EncodeString(ScenarioName, issueError=True)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State, Unit, Owner, Where):
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State, Unit, Owner, Where):
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number, Unit, Where, ForPlayer):
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player, Modifier, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(Unit, Owner, StartLocation, OrderType, DestLocation):
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    OrderType = EncodeOrder(OrderType, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, OrderType, 20)


def Comment(Text):
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count, Unit, Owner, Where, NewOwner):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    NewOwner = EncodePlayer(NewOwner, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(Count, Unit, Owner, Where, Percent):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count, Owner, Where, NewValue):
    Count = EncodeCount(Count, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(Add, Count, Unit, Owner, Where):
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Add, Unit, 53, Count, 20)


def PauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer():
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw():
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(Player, Status):
    Player = EncodePlayer(Player, issueError=True)
    Status = EncodeAllyStatus(Status, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)


def SetMemory(dest, modtype, value):
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, EPD(dest), value, 0, 45, modtype, 20)


def SetMemoryEPD(dest, modtype, value):
    dest = EncodePlayer(dest, issueError=True)
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, dest, value, 0, 45, modtype, 20)


def SetNextPtr(trg, dest):
    return SetMemory(trg + 4, 7, dest)


def SetDeathsX(Player, Modifier, Number, Unit, Mask):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx="SC")


def SetMemoryX(dest, modtype, value, mask):
    modtype = EncodeModifier(modtype, issueError=True)
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)


def SetMemoryXEPD(epd, modtype, value, mask):
    modtype = EncodeModifier(modtype, issueError=True)
    return SetDeathsX(epd, modtype, value, 0, mask)


def SetKills(Player, Modifier, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    if isinstance(Player, int) and Player >= 12:
        if Player == 13:
            return [
                SetMemory(0x6509B0, Add, -12 * 228),
                SetDeaths(CurrentPlayer, Modifier, Number, Unit),
                SetMemory(0x6509B0, Add, 12 * 228),
            ]
        ep_assert(
            Player <= 11, _("SetKills Player should be only P1~P12 or CurrentPlayer")
        )
    if isinstance(Unit, int):
        ep_assert(Unit <= 227, _("SetKills Unit should be at most 227"))
    return SetDeaths(Player - 228 * 12, Modifier, Number, Unit)
