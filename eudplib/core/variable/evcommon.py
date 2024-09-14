#!/usr/bin/python
from ...utils import EPD
from ..allocator import Forward
from ..rawtrigger import Add, SetTo
from .eudv import EUDCreateVariables
from .eudxv import EUDXVariable

_ev = EUDCreateVariables(5)
_xv = [EUDXVariable(0, SetTo, 0, 0) for _ in range(1)]
_addor = EUDXVariable(0, Add, 0)
_selfadder_valueaddr = Forward()
_selfadder = EUDXVariable(EPD(_selfadder_valueaddr), Add, 0)
_selfadder_valueaddr << _selfadder.getValueAddr()
