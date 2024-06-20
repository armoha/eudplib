#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


import sys
import warnings

from ..localize import _


class EPError(Exception):
    pass


# fmt: off
_ERR = _("Must put Trigger into onPluginStart, beforeTriggerExec or afterTriggerExec")  # noqa: E501
# fmt: on


class TriggerScopeError(EPError):
    def __init__(self, msg=_ERR, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class EPWarning(Warning):
    pass


def ep_assert(statement: object, message: object = "Assertion failed") -> None:
    if not statement:
        raise EPError(message)


def ep_eprint(*args: object, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def ep_warn(message: str) -> None:
    warnings.warn(message, EPWarning)
