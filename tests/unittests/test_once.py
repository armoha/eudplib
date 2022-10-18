from helper import *

a = EUDVariable(0)
b = EUDVariable(0)
i = EUDVariable(0)


@EUDFunc
def f_func_with_side_effect(b):
    global a
    a += 1
    return b


@TestInstance
def test_once():
    global a, b, i
    a << 0
    i << 0
    # repeat once block multiple times
    if EUDWhile()(i <= 9):
        if EUDExecuteOnce()():
            f_func_with_side_effect(0)
        EUDEndExecuteOnce()
        EUDSetContinuePoint()
        i += 1
    EUDEndWhile()
    test_equality("EUDExecuteOnce w. (true)", [a, i], [1, 10])

    a << 0
    b << 0
    i << 0
    if EUDWhile()(i <= 9):
        if EUDExecuteOnce()(f_func_with_side_effect(1)):
            b += 1
        EUDEndExecuteOnce()
        EUDSetContinuePoint()
        i += 1
    EUDEndWhile()
    test_equality("EUDExecuteOnce w. (true (side_effect)", [a, b], [1, 1])

    a << 0
    b << 0
    i << 0
    if EUDWhile()(i <= 9):
        if EUDExecuteOnce()(f_func_with_side_effect(0), neg=True):
            b += 1
        EUDEndExecuteOnce()
        EUDSetContinuePoint()
        i += 1
    EUDEndWhile()
    test_equality("EUDExecuteOnce w. (false (side_effect)", [a, b], [1, 1])
