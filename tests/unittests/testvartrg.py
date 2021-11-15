from helper import *


@TestInstance
def test_vdefval():
    a = EUDVariable(5)
    test_equality("Variable with default value", a, 5)


@TestInstance
def test_vmixedtrg():
    # VMixed actions
    a = EUDVariable()

    a << 0
    DoActions(SetDeaths(a, SetTo, EPD(a), 0))
    a << 1
    DoActions(SetDeaths(a, SetTo, f_mul(a, 30), 0))
    a << 2
    DoActions(SetDeaths(a, SetTo, a - 50, 0))
    DoActions(SetDeaths(3, SetTo, 123, a), SetDeaths(a, SetTo, a, a))

    test_assert(
        "Variable mixed trigger test",
        [
            Deaths(0, Exactly, 0x3FE9D727, 0),  # EPD(0) == 0x3fe9d727
            Deaths(1, Exactly, 30, 0),
            Deaths(2, Exactly, -48, 0),
            Deaths(3, Exactly, 123, 2),
            Deaths(2, Exactly, 2, 2),
        ],
    )

    DoActions(SetDeaths(AllPlayers, SetTo, 0, 0), SetDeaths(AllPlayers, SetTo, 0, 2))
    a <<= 1
