# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from collections.abc import Callable
from typing import NoReturn

from eudplib.localize import _


class CtrlStruOpener:
    def __init__(self, f: Callable) -> None:
        self._f: Callable = f
        self._called = False

    def __del__(self) -> None:
        if not self._called:
            raise RuntimeError(
                _("Control structures must be double-parenthesised.")
                + "\n ex) EUDInfLoop()()"
            )

    def __bool__(self) -> NoReturn:
        raise RuntimeError(
            _("Control structures must be double-parenthesised.")
            + "\n ex) EUDInfLoop()()"
        )

    def __call__(self, *args, **kwargs):
        self._called = True
        return self._f(*args, **kwargs)
