#!/usr/bin/python
from ...utils import EPD
from ..allocator import Forward
from ..rawtrigger import Add, SetTo
from .eudv import EUDCreateVariables, EUDVariable
from .eudxv import EUDXVariable

_ev = EUDCreateVariables(5)
_xv = [EUDXVariable(0, 0) for _ in range(1)]
_cp = [EUDVariable(EPD(0x6509B0), SetTo, 0) for _ in range(1)]
_selfadder_valueaddr = Forward()
_selfadder = EUDVariable(EPD(_selfadder_valueaddr), Add, 0)
_selfadder_valueaddr << _selfadder.getValueAddr()
