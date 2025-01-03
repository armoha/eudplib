# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .allocator import (
    CompressPayload,
    ConstExpr,
    CreatePayload,
    Evaluate,
    Forward,
    GetObjectAddr,
    IsConstExpr,
    RegisterCreatePayloadCallback,
    RlocInt,
    RlocInt_C,
    ShufflePayload,
    toRlocInt,
)
from .calcf.bitwise import (
    f_bitand,
    f_bitlshift,
    f_bitnand,
    f_bitnor,
    f_bitnot,
    f_bitnxor,
    f_bitor,
    f_bitrshift,
    f_bitsplit,
    f_bitxor,
)
from .calcf.muldiv import f_div, f_mul
from .curpl import AddCurrentPlayer, SetCurrentPlayer
from .eudfunc.eudf import (
    EUDFunc,
    EUDTypedFunc,
)
from .eudfunc.eudfmethod import (
    EUDMethod,
    EUDTypedMethod,
)
from .eudfunc.eudfptr import EUDFuncPtr, EUDTypedFuncPtr
from .eudfunc.eudfuncn import EUDReturn
from .eudobj import Db, EUDObject
from .eudstruct import (
    EUDStruct,
    EUDVArray,
    selftype,
)
from .inlinens import (
    EUDClearNamespace,
    EUDRegistered,
    EUDRegisterObjectToNamespace,
    GetEUDNamespace,
)
from .mapdata import (
    TBL,
    GetChkTokenized,
    GetLocationIndex,
    GetPlayerInfo,
    GetPropertyIndex,
    GetStringIndex,
    GetSwitchIndex,
    GetUnitIndex,
    IsMapdataInitialized,
    UnitProperty,
)
from .rawtrigger import (
    Accumulate,
    Action,
    Add,
    All,
    AlliedVictory,
    Ally,
    Always,
    AtLeast,
    AtMost,
    Attack,
    Bring,
    Buildings,
    CenterView,
    Clear,
    Cleared,
    Command,
    CommandLeast,
    CommandLeastAt,
    CommandMost,
    CommandMostAt,
    Comment,
    Condition,
    CountdownTimer,
    CreateUnit,
    CreateUnitWithProperties,
    Custom,
    Deaths,
    DeathsX,
    Defeat,
    Disable,
    Disabled,
    DisplayText,
    Draw,
    ElapsedTime,
    Enable,
    EncodeAIScript,
    EncodeAllyStatus,
    EncodeButtonSet,
    EncodeComparison,
    EncodeCount,
    EncodeFlingy,
    EncodeIcon,
    EncodeImage,
    EncodeIscript,
    EncodeLocation,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodePortrait,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSprite,
    EncodeString,
    EncodeSwitch,
    EncodeSwitchAction,
    EncodeSwitchState,
    EncodeTBL,
    EncodeTech,
    EncodeUnit,
    EncodeUnitOrder,
    EncodeUpgrade,
    EncodeWeapon,
    Enemy,
    Exactly,
    Gas,
    GetTriggerCounter,
    GiveUnits,
    HighestScore,
    Icon,
    Iscript,
    Kills,
    KillsAndRazings,
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
    LeastKills,
    LeastResources,
    LowestScore,
    Memory,
    MemoryEPD,
    MemoryX,
    MemoryXEPD,
    MinimapPing,
    ModifyUnitEnergy,
    ModifyUnitHangarCount,
    ModifyUnitHitPoints,
    ModifyUnitResourceAmount,
    ModifyUnitShields,
    MostKills,
    MostResources,
    Move,
    MoveLocation,
    MoveUnit,
    MuteUnitSpeech,
    Never,
    NextTrigger,
    Opponents,
    Order,
    Ore,
    OreAndGas,
    Patrol,
    PauseGame,
    PauseTimer,
    PlayWAV,
    PopTriggerScope,
    Portrait,
    PreserveTrigger,
    PushTriggerScope,
    Random,
    RawTrigger,
    Razings,
    RemoveUnit,
    RemoveUnitAt,
    RunAIScript,
    RunAIScriptAt,
    Score,
    Set,
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
    SetNextTrigger,
    SetResources,
    SetScore,
    SetSwitch,
    SetTo,
    StatText,
    Subtract,
    Switch,
    TalkingPortrait,
    Toggle,
    Total,
    Transmission,
    TrgAIScript,
    TrgAllyStatus,
    TrgComparison,
    TrgCount,
    TrgLocation,
    TrgModifier,
    TrgOrder,
    TrgProperty,
    TrgPropState,
    TrgResource,
    TrgScore,
    TrgString,
    TrgSwitch,
    TrgSwitchAction,
    TrgSwitchState,
    Units,
    UnitsAndBuildings,
    UnMuteUnitSpeech,
    UnpauseGame,
    UnpauseTimer,
    Victory,
    Wait,
)
from .variable import (
    EP_SetRValueStrictMode,
    EUDCreateVariables,
    EUDLightBool,
    EUDLightVariable,
    EUDVariable,
    EUDXVariable,
    IsEUDVariable,
    NonSeqCompute,
    SeqCompute,
    SetVariables,
    VProc,
)

__all__ = [
    "CompressPayload",
    "ConstExpr",
    "CreatePayload",
    "Evaluate",
    "Forward",
    "GetObjectAddr",
    "IsConstExpr",
    "RegisterCreatePayloadCallback",
    "RlocInt",
    "RlocInt_C",
    "ShufflePayload",
    "toRlocInt",
    "f_bitand",
    "f_bitlshift",
    "f_bitnand",
    "f_bitnor",
    "f_bitnot",
    "f_bitnxor",
    "f_bitor",
    "f_bitrshift",
    "f_bitsplit",
    "f_bitxor",
    "f_div",
    "f_mul",
    "AddCurrentPlayer",
    "SetCurrentPlayer",
    "EUDFunc",
    "EUDFuncPtr",
    "EUDMethod",
    "EUDReturn",
    "EUDTypedFunc",
    "EUDTypedFuncPtr",
    "EUDTypedMethod",
    "Db",
    "EUDObject",
    "EUDStruct",
    "EUDVArray",
    "selftype",
    "EUDClearNamespace",
    "EUDRegistered",
    "EUDRegisterObjectToNamespace",
    "GetEUDNamespace",
    "TBL",
    "GetChkTokenized",
    "GetLocationIndex",
    "GetPlayerInfo",
    "GetPropertyIndex",
    "GetStringIndex",
    "GetSwitchIndex",
    "GetUnitIndex",
    "IsMapdataInitialized",
    "UnitProperty",
    "Accumulate",
    "Action",
    "Add",
    "All",
    "AlliedVictory",
    "Ally",
    "Always",
    "AtLeast",
    "AtMost",
    "Attack",
    "Bring",
    "Buildings",
    "CenterView",
    "Clear",
    "Cleared",
    "Command",
    "CommandLeast",
    "CommandLeastAt",
    "CommandMost",
    "CommandMostAt",
    "Comment",
    "Condition",
    "CountdownTimer",
    "CreateUnit",
    "CreateUnitWithProperties",
    "Custom",
    "Deaths",
    "DeathsX",
    "Defeat",
    "Disable",
    "Disabled",
    "DisplayText",
    "Draw",
    "ElapsedTime",
    "Enable",
    "EncodeAIScript",
    "EncodeAllyStatus",
    "EncodeButtonSet",
    "EncodeComparison",
    "EncodeCount",
    "EncodeFlingy",
    "EncodeIcon",
    "EncodeImage",
    "EncodeIscript",
    "EncodeLocation",
    "EncodeModifier",
    "EncodeOrder",
    "EncodePlayer",
    "EncodePortrait",
    "EncodeProperty",
    "EncodePropState",
    "EncodeResource",
    "EncodeScore",
    "EncodeSprite",
    "EncodeString",
    "EncodeSwitch",
    "EncodeSwitchAction",
    "EncodeSwitchState",
    "EncodeTBL",
    "EncodeTech",
    "EncodeUnit",
    "EncodeUnitOrder",
    "EncodeUpgrade",
    "EncodeWeapon",
    "Enemy",
    "Exactly",
    "Gas",
    "GetTriggerCounter",
    "GiveUnits",
    "HighestScore",
    "Icon",
    "Iscript",
    "Kills",
    "KillsAndRazings",
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
    "LeastKills",
    "LeastResources",
    "LowestScore",
    "Memory",
    "MemoryEPD",
    "MemoryX",
    "MemoryXEPD",
    "MinimapPing",
    "ModifyUnitEnergy",
    "ModifyUnitHangarCount",
    "ModifyUnitHitPoints",
    "ModifyUnitResourceAmount",
    "ModifyUnitShields",
    "MostKills",
    "MostResources",
    "Move",
    "MoveLocation",
    "MoveUnit",
    "MuteUnitSpeech",
    "Never",
    "NextTrigger",
    "Opponents",
    "Order",
    "Ore",
    "OreAndGas",
    "Patrol",
    "PauseGame",
    "PauseTimer",
    "PlayWAV",
    "PopTriggerScope",
    "Portrait",
    "PreserveTrigger",
    "PushTriggerScope",
    "Random",
    "RawTrigger",
    "Razings",
    "RemoveUnit",
    "RemoveUnitAt",
    "RunAIScript",
    "RunAIScriptAt",
    "Score",
    "Set",
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
    "SetNextTrigger",
    "SetResources",
    "SetScore",
    "SetSwitch",
    "SetTo",
    "StatText",
    "Subtract",
    "Switch",
    "TalkingPortrait",
    "Toggle",
    "Total",
    "Transmission",
    "TrgAIScript",
    "TrgAllyStatus",
    "TrgComparison",
    "TrgCount",
    "TrgLocation",
    "TrgModifier",
    "TrgOrder",
    "TrgProperty",
    "TrgPropState",
    "TrgResource",
    "TrgScore",
    "TrgString",
    "TrgSwitch",
    "TrgSwitchAction",
    "TrgSwitchState",
    "Units",
    "UnitsAndBuildings",
    "UnMuteUnitSpeech",
    "UnpauseGame",
    "UnpauseTimer",
    "Victory",
    "Wait",
    "EP_SetRValueStrictMode",
    "EUDCreateVariables",
    "EUDLightBool",
    "EUDLightVariable",
    "EUDVariable",
    "EUDXVariable",
    "IsEUDVariable",
    "NonSeqCompute",
    "SeqCompute",
    "SetVariables",
    "VProc",
]
