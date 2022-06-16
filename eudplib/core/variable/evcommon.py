from .eudv import EUDVariable, EUDCreateVariables
from .eudxv import EUDXVariable
from ...utils import EPD
from ..rawtrigger import Add
from ..allocator import Forward

_ev = EUDCreateVariables(5)
_xv = [EUDXVariable(0, 0) for _ in range(1)]
_cp = [EUDVariable(EPD(0x6509B0), initval=0) for _ in range(1)]
_selfadder_valueaddr = Forward()
_selfadder = EUDVariable(EPD(_selfadder_valueaddr), Add, 0)
_selfadder_valueaddr << _selfadder.getValueAddr()
