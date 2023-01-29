#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.


import sys
import warnings


class EPError(Exception):
    pass


class TriggerScopeError(EPError):
    pass


class EPWarning(Warning):
    pass


def ep_assert(statement: object, message: object = "Assertion failed") -> None:
    if not statement:
        raise EPError(message)


def ep_eprint(*args: object, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def ep_warn(message: str) -> None:
    warnings.warn(message, EPWarning)
