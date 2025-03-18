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

__version__ = "0.80.2"

from .prelude import *
# TODO: remove lines below
from .core import *
from .utils import *
from .trigger import *
from .ctrlstru import *
from .epscript import *
from .memio import *
from .collections import *
from .scdata import (
    CSprite, EPDCUnitMap,
    Player1, Player2, Player3, Player4, Player5, Player6,
    Player7, Player8, Player9, Player10, Player11, Player12,
)
from .eudlib.mathf.div import f_div_euclid, f_div_floor, f_div_towards_zero
from .eudlib.utilf.gametick import f_getgametick
from .eudlib.utilf.listloop import (
    EUDLoopList,
    EUDLoopNewUnit,
    EUDLoopPlayerUnit,
    EUDLoopUnit,
    EUDLoopUnit2,
)
from .eudlib.utilf.pexist import (
    EUDEndPlayerLoop,
    EUDPlayerLoop,
)
from .string import *
from .string.cpprint import f_cpstr_adddw, f_cpstr_addptr, f_cpstr_addstr
from .maprw import *
from .qgc import *
from .trigtrg.runtrigtrg import (
    GetFirstTrigTrigger,
    GetLastTrigTrigger,
    RunTrigTrigger,
    TrigTriggerBegin,
    TrigTriggerEnd,
)

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
