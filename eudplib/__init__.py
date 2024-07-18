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

from .prelude import *
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
from .memio import *
from .eudlib import *
from .maprw import *
from .offsetmap import CSprite, EPDCUnitMap
from .offsetmap.cunit import EUDLoopCUnit, EUDLoopNewCUnit, EUDLoopPlayerCUnit
from .offsetmap.scdata import (
    Player1, Player2, Player3, Player4, Player5, Player6,
    Player7, Player8, Player9, Player10, Player11, Player12,
)
from .scdata import (
    FlingyData,
    ImageData,
    PlayerData,
    SpriteData,
    UnitData,
    UnitOrderData,
    WeaponData,
)
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
