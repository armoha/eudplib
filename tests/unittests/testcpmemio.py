from helper import *


@TestInstance
def test_cpmemio():
    a = Db(i2b4(0x1234) + i2b4(0x5678) + i2b4(0x9ABC))

    f_setcurpl(EPD(a))

    # Normal reading
    ptr, epd = f_dwepdread_cp(0)
    test_equality(
        "f_dwread_cp with cpo=0", [ptr, 0x58A364 + 4 * epd], [0x1234, 0x1234]
    )

    a, b, c = (f_dwread_cp(0), f_dwread_cp(1), f_dwread_cp(2))

    test_equality("f_dwread_cp", [a, b, c], [0x1234, 0x5678, 0x9ABC])

    # Issue #4: This should at least compile.
    v = EUDVariable(0)
    f_dwepdread_cp(v)

    # Writing
    f_dwwrite_cp(1, 0x1111)
    a, b, c = (f_dwread_cp(0), f_dwread_cp(1), f_dwread_cp(2))

    test_equality("f_dwread_cp", [a, b, c], [0x1234, 0x1111, 0x9ABC])

    # byte/word reading
    f_dwadd_cp(0, 0xABCD0000)
    a, b, c = (f_wread_cp(0, 3), f_wread_cp(1, 1), f_bread_cp(2, 1))
    test_equality("f_wread_cp & f_bread_cp", [a, b, c], [0x11AB, 0x11, 0x9A])

    # byte/word writing
    f_wwrite_cp(0, 1, 0x4567)
    f_wwrite_cp(1, 2, 0x8765)
    f_bwrite_cp(2, 1, 0x46)
    a, b, c = (f_wread_cp(0, 2), f_bread_cp(1, 3), f_bread_cp(2, 1))
    test_equality("f_bwrite_cp & f_wwrite_cp", [a, b, c], [0xAB45, 0x87, 0x46])

    f_setcurpl(P1)
