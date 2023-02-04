from helper import *


@EUDFunc
def f1(a):
    ret = EUDVariable(0)
    if EUDIf()(a == 0):
        ret << 1234
    if EUDElse()():
        ret << 5678
    EUDEndIf()

    return ret


@EUDFunc
def f2(a):
    if EUDIf()(a == 0):
        EUDReturn(1234)
    if EUDElseIf()(a == 1):
        EUDReturn(5678)
    EUDEndIf()
    return 9012


@TestInstance
def test_multret():
    # a, b = f1(0), f1(1)
    a, b = EUDCreateVariables(2)
    f1(0, ret=[a])
    f1(1, ret=[b])
    c, d, e = f2(0), f2(1), f2(2)
    test_assert(
        "Multiple EUDReturn test",
        [a == 1234, b == 5678, c == 1234, d == 5678, e == 9012],
    )
