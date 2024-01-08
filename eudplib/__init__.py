#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: I001
# fmt: off

import builtins
import keyword
import types

__version__ = "0.76.15"

from .prelude import (
    f_div,
    EUDVariable, EUDCreateVariables, SetVariables,
    VProc,
    Db,
    RawTrigger, PreserveTrigger,
    UnitProperty, Disabled,
    # EUDFunc
    EUDFunc, EUDTypedFunc, EUDFuncPtr, EUDTypedFuncPtr,
    EUDMethod, EUDTypedMethod, EUDReturn,
    # EUDStruct
    EUDStruct, EUDVArray, selftype,
    # ConstType
    Weapon, Flingy, Sprite, Image, Iscript,
    Portrait, Icon, Upgrade, Tech,
    UnitOrder, StatText,
    TrgAIScript, TrgAllyStatus, TrgComparison, TrgCount,
    TrgLocation, TrgModifier, TrgOrder, TrgPlayer, TrgProperty,
    TrgPropState, TrgResource, TrgScore, TrgString, TrgSwitch,
    TrgSwitchAction, TrgSwitchState, TrgUnit,
    # TrgPlayer
    P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12,
    Force1, Force2, Force3, Force4, AllPlayers, CurrentPlayer,
    Allies, Foes, NeutralPlayers, NonAlliedVictoryPlayers,
    # Condition
    Always, Never,
    Accumulate, Bring,
    Command, CommandLeast, CommandLeastAt, CommandMost, CommandMostAt,
    CountdownTimer, ElapsedTime,
    Deaths, DeathsX, Kills,
    Memory, MemoryEPD, MemoryX, MemoryXEPD,
    HighestScore, MostKills, MostResources,
    LowestScore, LeastKills, LeastResources,
    Opponents,
    Score, Switch,
    # Action
    SetCurrentPlayer,
    CenterView, CreateUnit, CreateUnitWithProperties, Comment,
    Defeat, DisplayText, Draw,
    GiveUnits,
    KillUnit, KillUnitAt,
    LeaderBoardComputerPlayers,
    LeaderBoardControl, LeaderBoardGoalControl,
    LeaderBoardControlAt, LeaderBoardGoalControlAt,
    LeaderBoardGreed, LeaderBoardResources, LeaderBoardGoalResources,
    LeaderBoardKills, LeaderBoardGoalKills,
    LeaderBoardScore, LeaderBoardGoalScore,
    MinimapPing,
    ModifyUnitEnergy, ModifyUnitHangarCount, ModifyUnitHitPoints,
    ModifyUnitResourceAmount, ModifyUnitShields,
    MoveLocation, MoveUnit,
    Order,
    MuteUnitSpeech, PauseGame, PauseTimer,
    UnMuteUnitSpeech, UnpauseGame, UnpauseTimer,
    PlayWAV,
    RemoveUnit, RemoveUnitAt,
    RunAIScript, RunAIScriptAt,
    SetAllianceStatus, SetCountdownTimer,
    SetDeaths, SetDeathsX, SetKills,
    SetDoodadState, SetInvincibility,
    SetMemory, SetMemoryEPD, SetMemoryX, SetMemoryXEPD,
    SetMissionObjectives, SetNextScenario,
    SetResources, SetScore, SetSwitch,
    TalkingPortrait, Transmission,
    Victory,
    Wait,
    # TrgResource
    Ore, Gas, OreAndGas,
    # TrgAllyStatus
    Ally, Enemy, AlliedVictory,
    # TrgOrder
    Attack, Move, Patrol,
    # TrgScore
    Units, Buildings, UnitsAndBuildings,
    Razings, KillsAndRazings, Total, Custom,
    # TrgComparison
    AtLeast, AtMost, Exactly,
    # TrgModifier
    Add, Subtract, SetTo,
    # TrgPropState
    Enable, Disable, Toggle,
    # TrgSwitchState
    Set, Cleared,
    # TrgSwitchAction
    Clear, Random,
    # TrgCount
    All,
)
from .core import (
    TBL, Action, AddCurrentPlayer,
    CompressPayload, Condition, ConstExpr, CreatePayload,
    EncodeAIScript, EncodeAllyStatus, EncodeComparison, EncodeCount,
    EncodeFlingy, EncodeIcon, EncodeImage, EncodeIscript,
    EncodeLocation, EncodeModifier, EncodeOrder, EncodePlayer,
    EncodePortrait, EncodeProperty, EncodePropState, EncodeResource,
    EncodeScore, EncodeSprite, EncodeString, EncodeSwitch,
    EncodeSwitchAction, EncodeSwitchState, EncodeTBL, EncodeTech,
    EncodeUnit, EncodeUnitOrder, EncodeUpgrade, EncodeWeapon,
    EP_SetRValueStrictMode, ShufflePayload,
    EUDLightBool, EUDLightVariable, EUDObject, GetObjectAddr,
    EUDRegistered, EUDRegisterObjectToNamespace, EUDClearNamespace,
    EUDXVariable, Evaluate, Forward,
    GetChkTokenized, GetEUDNamespace, GetTriggerCounter,
    GetLocationIndex, GetPlayerInfo, GetPropertyIndex,
    GetStringIndex, GetSwitchIndex, GetUnitIndex,
    IsConstExpr, IsEUDVariable, RlocInt, RlocInt_C, toRlocInt,
    IsMapdataInitialized,
    Player1, Player2, Player3, Player4, Player5, Player6,
    Player7, Player8, Player9, Player10, Player11, Player12,
    PopTriggerScope, PushTriggerScope,
    RegisterCreatePayloadCallback,
    SeqCompute, NonSeqCompute,
    NextTrigger, SetNextPtr, SetNextTrigger,
    f_bitand, f_bitlshift, f_bitnand, f_bitnor, f_bitnot,
    f_bitnxor, f_bitor, f_bitrshift, f_bitsplit, f_bitxor,
    f_mul,
)
from .ctrlstru import *
from .epscript import EPS_SetDebug, EPSLoader, epsCompile
from .eudlib import *
from .maprw import *
from .offsetmap import CSprite, CUnit, EPDCUnitMap
from .trigger import *
from .trigtrg.runtrigtrg import (
    GetFirstTrigTrigger,
    GetLastTrigTrigger,
    RunTrigTrigger,
    TrigTriggerBegin,
    TrigTriggerEnd,
)
from .utils import *

# remove modules from __all__
_old_globals = [
    "keyword",
    "__file__",
    "types",
    "__doc__",
    "__version__",
    "builtins",
    "__cached__",
    "__name__",
    "__loader__",
    "__spec__",
    "__path__",
    "__package__",
    "__builtins__",
]
_alllist = []
for _k, _v in dict(globals()).items():
    if _k in _old_globals:
        continue
    elif _k != "stocktrg" and isinstance(_v, types.ModuleType):
        continue
    elif _k[0] == "_":
        continue
    _alllist.append(_k)

__all__ = _alllist

del _k
del _v


def eudplibVersion():  # noqa: N802
    return __version__


_alllist.append("eudplibVersion")


from .epscript import epscompile

epscompile._set_eps_globals(_alllist)
epscompile._set_py_keywords(keyword.kwlist)
epscompile._set_py_builtins(dir(builtins))
