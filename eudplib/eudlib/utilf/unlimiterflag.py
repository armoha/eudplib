#!/usr/bin/python
from dataclasses import dataclass


@dataclass
class _UnlimiterBool:
    is_unlimiter_on: bool = False


_unlimiter: _UnlimiterBool = _UnlimiterBool(is_unlimiter_on=False)


def _turnUnlimiterOn() -> None:
    global _unlimiter
    _unlimiter.is_unlimiter_on = True


def IsUnlimiterOn() -> bool:
    global _unlimiter
    return _unlimiter.is_unlimiter_on == True
