from helper import *

import eudplib.core.variable.eudv as ev
import inspect

_frames = {}
original_init = ev.EUDVariable.__init__


def _patched_init(self, *args, **kwargs):
    _frames[0] = inspect.currentframe().f_back  # 이 줄
    return original_init(self, *args, **kwargs)


ev.EUDVariable.__init__ = _patched_init


@TestInstance
def test_blockstru():
    # LoopN
    i = EUDVariable(0)
    if EUDLoopN()(5):
        i += 1
    EUDEndLoopN()
    test_assert("EUDLoopN test", i == 5)

    # While
    i, j = EUDCreateVariables(2)
    if EUDWhileNot()(i >= 100):
        i += 1
        j += 3
    EUDEndWhile()
    test_assert("EUDWhile test", j == 300)
