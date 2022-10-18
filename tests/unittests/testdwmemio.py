import random

from helper import *


@TestInstance
def test_dwmemio():
    a = Db(i2b4(0x1234))

    # Normal reading
    ptr, epd = f_dwepdread_epd(EPD(a))

    # For any ptr, there are 4 valid epd values. So comparing epd and epd
    # for equality won't work. Here we convert epd back to ptr for comparison.
    test_equality("f_dwread_epd", [ptr, 0x58A364 + 4 * epd], [0x1234, 0x1234])

    # Map position reading
    b1 = random.randint(0, 0xFFFFFFFF)
    dim = GetChkTokenized().getsection("DIM")
    bx, by = b2i2(dim), b2i2(dim, 2)
    bx = 2 ** ((bx - 1).bit_length() + 5) - 1
    by = 2 ** ((by - 1).bit_length() + 5) - 1
    bx, by = b1 & bx, (b1 & (by << 16)) >> 16

    x, y = f_posread_epd(EPD(Db(i2b4(b1))))
    test_equality("f_posread_epd %X" % b1, [x, y], [bx, by])

    # CUnit reading
    c1 = random.randint(0, 0xFFFFFFFF)
    if c1 == 0:
        cptr, cepd = 0, 0
    else:
        cptr, cepd = 0x400008, 0xFFF9D729
        for bit in range(4, 22):
            bit = 1 << bit
            if c1 & bit:
                cptr += bit
                cepd += bit >> 2
        cepd = cepd & 0xFFFFFFFF

    ptr, epd = f_cunitepdread_epd(EPD(Db(i2b4(c1))))
    test_equality("f_cunitread_epd %X" % c1, [ptr, epd], [cptr, cepd])

    # Flag reading!
    f1, f2, f3, f4 = f_flagread_epd(EPD(a), 0x1000, 0x0100, ~0x0010, 0x0004)
    test_equality("f_flagread_epd", [f1, f2, f3, f4], [0x1000, 0x0000, 0x1224, 0x0004])

    # dwwrite
    f_dwwrite_epd(EPD(a), 1234)
    test_assert("f_dwwrite works", Memory(a, Exactly, 1234))

    # Fixes euddraft/issues#4
    f_setcurpl(EPD(a))
    f_dwsubtract_cp(0, 12)
    f_setcurpl(Player1)
    test_assert("f_dwwrite works", Memory(a, Exactly, 1222))

    f_randomize()
    f_rand()
    EP_SetRValueStrictMode(False)
    f_dwrand()
    EP_SetRValueStrictMode(True)

    # Fixes https://cafe.naver.com/edac/81090
    SetKills(CurrentPlayer, SetTo, 0, 0)
