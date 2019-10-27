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

from .rawtriggerdef import Disabled, RawTrigger, GetTriggerCounter
from .triggerscope import PushTriggerScope, PopTriggerScope, NextTrigger, SetNextTrigger

from .condition import Condition
from .action import Action

# fmt: off
from .stockcond import (
    CountdownTimer, Command, Bring, Accumulate, Kills,
    CommandMost, CommandMostAt, MostKills, HighestScore, MostResources,
    Switch, ElapsedTime, Opponents, Deaths, CommandLeast,
    CommandLeastAt, LeastKills, LowestScore, LeastResources, Score,
    Always, Never, Memory, MemoryEPD,
    DeathsX, MemoryX, MemoryXEPD,
)

from .stockact import (
    Victory, Defeat, PreserveTrigger, Wait, PauseGame,
    UnpauseGame, Transmission, PlayWAV, DisplayText, CenterView,
    CreateUnitWithProperties, SetMissionObjectives, SetSwitch,
    SetCountdownTimer, RunAIScript, RunAIScriptAt, LeaderBoardControl,
    LeaderBoardControlAt, LeaderBoardResources, LeaderBoardKills,
    LeaderBoardScore, KillUnit, KillUnitAt, RemoveUnit, RemoveUnitAt,
    SetResources, SetScore, MinimapPing, TalkingPortrait, MuteUnitSpeech,
    UnMuteUnitSpeech, LeaderBoardComputerPlayers, LeaderBoardGoalControl,
    LeaderBoardGoalControlAt, LeaderBoardGoalResources,
    LeaderBoardGoalKills, LeaderBoardGoalScore, MoveLocation, MoveUnit,
    LeaderBoardGreed, SetNextScenario, SetDoodadState, SetInvincibility,
    CreateUnit, SetDeaths, Order, Comment, GiveUnits, ModifyUnitHitPoints,
    ModifyUnitEnergy, ModifyUnitShields, ModifyUnitResourceAmount,
    ModifyUnitHangarCount, PauseTimer, UnpauseTimer, Draw,
    SetAllianceStatus, SetMemory, SetNextPtr, SetMemoryEPD,
    SetDeathsX, SetMemoryX, SetMemoryXEPD, SetKills,
)

from .constenc import (
    All, Enemy, Ally, AlliedVictory, AtLeast, AtMost, Exactly, SetTo, Add,
    Subtract, Move, Patrol, Attack, P1, P2, P3, P4, P5, P6, P7, P8, P9,
    P10, P11, P12, Player1, Player2, Player3, Player4, Player5, Player6,
    Player7, Player8, Player9, Player10, Player11, Player12,
    CurrentPlayer, Foes, Allies, NeutralPlayers, AllPlayers, Force1,
    Force2, Force3, Force4, NonAlliedVictoryPlayers, Enable, Disable,
    Toggle, Ore, Gas, OreAndGas, Total, Units, Buildings,
    UnitsAndBuildings, Kills, Razings, KillsAndRazings, Custom, Set,
    Clear, Random, Cleared,

    # encoders
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
)
# fmt: on
from .strenc import (
    EncodeAIScript,
    EncodeLocation,
    EncodeLocationIndex,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
    EncodeTBL,
)
