from helper import *


@TestInstance
def test_operator_lvalue():
    a, b = EUDVariable(), EUDVariable()
    with expect_eperror():
        (a + b) << 5

    with expect_eperror():
        (a * b) << 5


@TestInstance
def test_function_lvalue():
    with expect_eperror():
        a = f_dwread_epd(0)
        a << 5


@TestInstance
def test_rvalue():
    v1 = EUDVariable(0)
    trg = NextTrigger()
    v2 = v1 + 1 + EUDVariable(2) + 3 + EUDVariable(4) + 5
    test_equality(
        "rvalue reuse test",
        [v2, f_dwread(trg + 344)],
        [15, EPD(v2.getValueAddr())],
    )
    with expect_eperror():
        SetVariables(f_dwread_epd(0), 0)
