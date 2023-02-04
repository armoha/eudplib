from helper import *


@TestInstance
def test_xvdefval():
    a = EUDXVariable(5, 19)
    test_equality("XVariable with default value", a, 5)
    test_assert("XVariable with default flag", [Deaths(EPD(a._varact), Exactly, 19, 0)])


@TestInstance
def test_xvmixedtrg():
    # VMixed actions
    a = EUDXVariable()

    a << 0
    DoActions(SetDeaths(a, SetTo, EPD(a), 0))
    a << 1
    DoActions(SetDeaths(a, SetTo, f_mul(a, 30), 0))
    a << 2
    DoActions(SetDeaths(a, SetTo, a - 50, 0))
    DoActions(SetDeaths(3, SetTo, 123, a), SetDeaths(a, SetTo, a, a))

    test_assert(
        "XVariable mixed trigger test",
        [
            Deaths(0, Exactly, 0x3FE9D727, 0),  # EPD(0) == 0x3fe9d727
            Deaths(1, Exactly, 30, 0),
            Deaths(2, Exactly, -48, 0),
            Deaths(3, Exactly, 123, 2),
            Deaths(2, Exactly, 2, 2),
        ],
    )

    DoActions(a.SetNumber(15), a.SetMask(19))
    DoActions(SetDeaths(a, SetTo, 40 // a, a))
    d1 = EUDVariable()
    d1 << a
    d2, d3 = f_div(40, a)

    test_equality("XVariable flag trigger test", [d1, d2, d3], [3, 13, 1])

    DoActions(
        SetDeaths(AllPlayers, SetTo, 0, 0),
        SetDeaths(AllPlayers, SetTo, 0, 2),
        SetDeaths(AllPlayers, SetTo, 0, 3),
    )
