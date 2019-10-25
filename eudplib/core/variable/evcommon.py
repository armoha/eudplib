from .eudv import EUDVariable, EUDCreateVariables
from .eudxv import EUDXVariable

_ev = EUDCreateVariables(3)
_xv = [EUDXVariable(0, 0) for _ in range(1)]
