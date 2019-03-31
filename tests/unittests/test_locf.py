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
    test_equality("Location functions test", [
        f_dwread_epd(EPD(0x58DC68)),
        f_dwread_epd(EPD(0x58DC6C)),
    ], [52, 74])

    Pos = Db(i2b4(0x6FE05BD))
    f_setloc_epd(loc, EPD(Pos))
    L, T = f_getlocTL(loc)
    test_equality(
        "f_setloc_epd test", [L, T], [0x5BD, 0x6FE]
    )
