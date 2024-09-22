# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from ..core.eudstruct.vararray import _EUDVArray


class PVariable(_EUDVArray):
    def __init__(self, initvars=None, *, _from=None) -> None:
        super().__init__(initvars, _from=_from, _size=8, _basetype=None)

    def __getitem__(self, i):
        return super().__getitem__(c.EncodePlayer(i))

    def __setitem__(self, i, value) -> None:
        super().__setitem__(c.EncodePlayer(i), value)
