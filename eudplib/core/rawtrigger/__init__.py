#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .action import Action
from .condition import Condition
from .constenc import (  # encoders
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
    Kills,
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
    TrgAllyStatus,
    TrgComparison,
    TrgCount,
    TrgModifier,
    TrgOrder,
    TrgPlayer,
    TrgProperty,
    TrgPropState,
    TrgResource,
    TrgScore,
    TrgSwitchAction,
    TrgSwitchState,
    Units,
    UnitsAndBuildings,
)
from .rawtriggerdef import Disabled, GetTriggerCounter, RawTrigger
from .stockact import (
    CenterView,
    Comment,
    CreateUnit,
    CreateUnitWithProperties,
    Defeat,
    DisplayText,
    Draw,
    GiveUnits,
    KillUnit,
    KillUnitAt,
    LeaderBoardComputerPlayers,
    LeaderBoardControl,
    LeaderBoardControlAt,
    LeaderBoardGoalControl,
    LeaderBoardGoalControlAt,
    LeaderBoardGoalKills,
    LeaderBoardGoalResources,
    LeaderBoardGoalScore,
    LeaderBoardGreed,
    LeaderBoardKills,
    LeaderBoardResources,
    LeaderBoardScore,
    MinimapPing,
    ModifyUnitEnergy,
    ModifyUnitHangarCount,
    ModifyUnitHitPoints,
    ModifyUnitResourceAmount,
    ModifyUnitShields,
    MoveLocation,
    MoveUnit,
    MuteUnitSpeech,
    Order,
    PauseGame,
    PauseTimer,
    PlayWAV,
    PreserveTrigger,
    RemoveUnit,
    RemoveUnitAt,
    RunAIScript,
    RunAIScriptAt,
    SetAllianceStatus,
    SetCountdownTimer,
    SetDeaths,
    SetDeathsX,
    SetDoodadState,
    SetInvincibility,
    SetKills,
    SetMemory,
    SetMemoryEPD,
    SetMemoryX,
    SetMemoryXEPD,
    SetMissionObjectives,
    SetNextPtr,
    SetNextScenario,
    SetResources,
    SetScore,
    SetSwitch,
    TalkingPortrait,
    Transmission,
    UnMuteUnitSpeech,
    UnpauseGame,
    UnpauseTimer,
    Victory,
    Wait,
)
from .stockcond import (
    Accumulate,
    Always,
    Bring,
    Command,
    CommandLeast,
    CommandLeastAt,
    CommandMost,
    CommandMostAt,
    CountdownTimer,
    Deaths,
    DeathsX,
    ElapsedTime,
    HighestScore,
    LeastKills,
    LeastResources,
    LowestScore,
    Memory,
    MemoryEPD,
    MemoryX,
    MemoryXEPD,
    MostKills,
    MostResources,
    Never,
    Opponents,
    Score,
    Switch,
)
from .strenc import (
    EncodeAIScript,
    EncodeFlingy,
    EncodeIcon,
    EncodeImage,
    EncodeIscript,
    EncodeLocation,
    EncodePortrait,
    EncodeSprite,
    EncodeString,
    EncodeSwitch,
    EncodeTBL,
    EncodeTech,
    EncodeUnit,
    EncodeUnitOrder,
    EncodeUpgrade,
    EncodeWeapon,
    Flingy,
    Icon,
    Image,
    Iscript,
    Portrait,
    Sprite,
    StatText,
    Tech,
    TrgAIScript,
    TrgLocation,
    TrgString,
    TrgSwitch,
    TrgUnit,
    UnitOrder,
    Upgrade,
    Weapon,
)
from .triggerscope import (
    NextTrigger,
    PopTriggerScope,
    PushTriggerScope,
    SetNextTrigger,
)

__all__ = [
    "Action",
    "Condition",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6",
    "P7",
    "P8",
    "P9",
    "P10",
    "P11",
    "P12",
    "Add",
    "All",
    "AlliedVictory",
    "Allies",
    "AllPlayers",
    "Ally",
    "AtLeast",
    "AtMost",
    "Attack",
    "Buildings",
    "Clear",
    "Cleared",
    "CurrentPlayer",
    "Custom",
    "Disable",
    "Enable",
    "EncodeAllyStatus",
    "EncodeComparison",
    "EncodeCount",
    "EncodeModifier",
    "EncodeOrder",
    "EncodePlayer",
    "EncodeProperty",
    "EncodePropState",
    "EncodeResource",
    "EncodeScore",
    "EncodeSwitchAction",
    "EncodeSwitchState",
    "Enemy",
    "Exactly",
    "Foes",
    "Force1",
    "Force2",
    "Force3",
    "Force4",
    "Gas",
    "Kills",
    "KillsAndRazings",
    "Move",
    "NeutralPlayers",
    "NonAlliedVictoryPlayers",
    "Ore",
    "OreAndGas",
    "Patrol",
    "Player1",
    "Player2",
    "Player3",
    "Player4",
    "Player5",
    "Player6",
    "Player7",
    "Player8",
    "Player9",
    "Player10",
    "Player11",
    "Player12",
    "Random",
    "Razings",
    "Set",
    "SetTo",
    "Subtract",
    "Toggle",
    "Total",
    "TrgAllyStatus",
    "TrgComparison",
    "TrgCount",
    "TrgModifier",
    "TrgOrder",
    "TrgPlayer",
    "TrgProperty",
    "TrgPropState",
    "TrgResource",
    "TrgScore",
    "TrgSwitchAction",
    "TrgSwitchState",
    "Units",
    "UnitsAndBuildings",
    "Disabled",
    "GetTriggerCounter",
    "RawTrigger",
    "CenterView",
    "Comment",
    "CreateUnit",
    "CreateUnitWithProperties",
    "Defeat",
    "DisplayText",
    "Draw",
    "GiveUnits",
    "KillUnit",
    "KillUnitAt",
    "LeaderBoardComputerPlayers",
    "LeaderBoardControl",
    "LeaderBoardControlAt",
    "LeaderBoardGoalControl",
    "LeaderBoardGoalControlAt",
    "LeaderBoardGoalKills",
    "LeaderBoardGoalResources",
    "LeaderBoardGoalScore",
    "LeaderBoardGreed",
    "LeaderBoardKills",
    "LeaderBoardResources",
    "LeaderBoardScore",
    "MinimapPing",
    "ModifyUnitEnergy",
    "ModifyUnitHangarCount",
    "ModifyUnitHitPoints",
    "ModifyUnitResourceAmount",
    "ModifyUnitShields",
    "MoveLocation",
    "MoveUnit",
    "MuteUnitSpeech",
    "Order",
    "PauseGame",
    "PauseTimer",
    "PlayWAV",
    "PreserveTrigger",
    "RemoveUnit",
    "RemoveUnitAt",
    "RunAIScript",
    "RunAIScriptAt",
    "SetAllianceStatus",
    "SetCountdownTimer",
    "SetDeaths",
    "SetDeathsX",
    "SetDoodadState",
    "SetInvincibility",
    "SetKills",
    "SetMemory",
    "SetMemoryEPD",
    "SetMemoryX",
    "SetMemoryXEPD",
    "SetMissionObjectives",
    "SetNextPtr",
    "SetNextScenario",
    "SetResources",
    "SetScore",
    "SetSwitch",
    "TalkingPortrait",
    "Transmission",
    "UnMuteUnitSpeech",
    "UnpauseGame",
    "UnpauseTimer",
    "Victory",
    "Wait",
    "Accumulate",
    "Always",
    "Bring",
    "Command",
    "CommandLeast",
    "CommandLeastAt",
    "CommandMost",
    "CommandMostAt",
    "CountdownTimer",
    "Deaths",
    "DeathsX",
    "ElapsedTime",
    "HighestScore",
    "LeastKills",
    "LeastResources",
    "LowestScore",
    "Memory",
    "MemoryEPD",
    "MemoryX",
    "MemoryXEPD",
    "MostKills",
    "MostResources",
    "Never",
    "Opponents",
    "Score",
    "Switch",
    "EncodeAIScript",
    "EncodeFlingy",
    "EncodeIcon",
    "EncodeImage",
    "EncodeIscript",
    "EncodeLocation",
    "EncodePortrait",
    "EncodeSprite",
    "EncodeString",
    "EncodeSwitch",
    "EncodeTBL",
    "EncodeTech",
    "EncodeUnit",
    "EncodeUnitOrder",
    "EncodeUpgrade",
    "EncodeWeapon",
    "Flingy",
    "Icon",
    "Image",
    "Iscript",
    "Portrait",
    "Sprite",
    "StatText",
    "Tech",
    "TrgAIScript",
    "TrgLocation",
    "TrgString",
    "TrgSwitch",
    "TrgUnit",
    "UnitOrder",
    "Upgrade",
    "Weapon",
    "NextTrigger",
    "PopTriggerScope",
    "PushTriggerScope",
    "SetNextTrigger",
]
