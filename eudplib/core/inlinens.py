# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from typing import Any

from eudplib.utils import ep_warn

from ..localize import _

_objns: dict[str, Any] = {}


def EUDClearNamespace() -> None:  # noqa: N802
    _objns.clear()


def EUDRegisterObjectToNamespace(funcname: str, obj: Any) -> Any:  # noqa: N802
    """Register object to inline code namespace."""
    if funcname[0] != "_":
        if funcname in _objns:
            err = _("Duplicated name {} for EUDRegisterObjectToNamespace")
            ep_warn(err.format(funcname))
            _objns[funcname] = None
        else:
            _objns[funcname] = obj

    return obj


def EUDRegistered(func):  # noqa: N802
    """Decorator for registering class / function."""
    return EUDRegisterObjectToNamespace(func.__name__, func)


def GetEUDNamespace() -> dict[str, Any]:  # noqa: N802
    """Get list of functions that inline code can use."""
    return _objns
