from helper import *


@EUDTracedFunc
def _t1(x):
    EUDTraceLog()
    if EUDIf()(x == 0):
        EUDTraceLog()
        EUDReturn(11)
    if EUDElseIf()(x == 1):
        EUDTraceLog()
        EUDReturn(12)
    EUDEndIf()
    EUDTraceLog()
    return 13


@EUDTracedFunc
def _t2():
    pass


@TestInstance
def test_trace():
    a = _t1(0)
    t1 = GetTraceStackDepth()
    b = _t1(1)
    t2 = GetTraceStackDepth()
    c = _t1(2)
    t3 = GetTraceStackDepth()
    test_equality("EUDTracedFunc works well", [a, b, c, t1, t2, t3], [11, 12, 13, 0, 0, 0])

    _t2()
    test_equality("EUDTraceFunc for function with no returns", GetTraceStackDepth(), 0)


# phu54321/euddraft#3
EUDTracedTypedMethod
