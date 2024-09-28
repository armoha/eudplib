# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from dataclasses import dataclass


@dataclass
class _UnlimiterBool:
    is_unlimiter_on: bool = False


_unlimiter: _UnlimiterBool = _UnlimiterBool(is_unlimiter_on=False)


def _turnUnlimiterOn() -> None:  # noqa: N802
    global _unlimiter
    _unlimiter.is_unlimiter_on = True


def IsUnlimiterOn() -> bool:  # noqa: N802
    global _unlimiter
    return _unlimiter.is_unlimiter_on is True
