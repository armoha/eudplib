from helper import *


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
