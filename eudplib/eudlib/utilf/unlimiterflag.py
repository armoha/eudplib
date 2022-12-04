from dataclasses import dataclass


@dataclass
class _UnlimiterBool:
    is_unlimiter_on: bool = False


_unlimiter = _UnlimiterBool(is_unlimiter_on=False)


def _turnUnlimiterOn():
    global _unlimiter
    _unlimiter.is_unlimiter_on = True


def IsUnlimiterOn():
    global _unlimiter
    return _unlimiter.is_unlimiter_on == True
