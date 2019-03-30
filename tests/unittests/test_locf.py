from helper import *


@TestInstance
def test_locf():
    loc = EUDVariable(0)

    f_setloc(loc, 32, 64)
    f_addloc(loc, 16, 8)
    f_dilateloc(loc, 4, 2)

    L, T = f_getlocTL(loc)

    test_equality(
        "f_getlocTL test", [L, T], [44, 70]
    )
    test_assert("Location functions test", [
        Memory(0x58DC60 + 8, Exactly, 52),
        Memory(0x58DC60 + 12, Exactly, 74),
    ])

    Pos = Db(i2b4(0x6FE05BD))
    f_setloc_epd(loc, EPD(Pos))
    L, T = f_getlocTL(loc)
    test_equality(
        "f_setloc_epd test", [L, T], [0x5BD, 0x6FE]
    )
