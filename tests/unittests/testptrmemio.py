from helper import *


@TestInstance
def test_ptr_read():
    a = Db(b"\x01\x02\x03\x04\x05\x06\x07\x08")

    # bread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    br0 = f_bread(a + 0)
    cp1 = f_getcurpl()
    br1 = f_bread(a + 3)
    cp2 = f_getcurpl()
    test_equality("f_bread", [cp0, br0, cp1, br1, cp2], [0, 1, 0, 4, 0])

    # wread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    wr0 = f_wread(a + 0)
    cp1 = f_getcurpl()
    wr1 = f_wread(a + 1)
    cp2 = f_getcurpl()
    wr2 = f_wread(a + 3)
    cp3 = f_getcurpl()
    test_equality(
        "f_wread",
        [cp0, wr0, cp1, wr1, cp2, wr2, cp3],
        [0, 0x0201, 0, 0x0302, 0, 0x0504, 0],
    )

    # dwread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    dwr0 = f_dwread(a + 0)
    cp1 = f_getcurpl()
    dwr1 = f_dwread(a + 1)
    cp2 = f_getcurpl()
    dwr2 = f_dwread(a + 3)
    cp3 = f_getcurpl()
    test_equality(
        "f_dwread",
        [cp0, dwr0, cp1, dwr1, cp2, dwr2, cp3],
        [0, 0x04030201, 0, 0x05040302, 0, 0x07060504, 0],
    )


@TestInstance
def test_ptr_write():
    # bwrite
    f_setcurpl(Player1)
    a = Db(b"\x01\x02\x03\x04\x05\x06\x07\x08")
    cp0 = f_getcurpl()
    f_bwrite(a + 0, 5)
    cp1 = f_getcurpl()
    f_bwrite(a + 3, 7)
    cp2 = f_getcurpl()
    test_equality(
        "f_bwrite",
        [f_dwread_epd(EPD(a)), f_dwread_epd(EPD(a) + 1), cp0, cp1, cp2],
        [0x07030205, 0x08070605, 0, 0, 0],
    )

    # wwrite
    f_setcurpl(Player1)
    a = Db(b"\x01\x02\x03\x04\x05\x06\x07\x08")
    cp0 = f_getcurpl()
    f_wwrite(a + 0, 0xAABB)
    cp1 = f_getcurpl()
    f_wwrite(a + 3, 0xCCDD)
    cp2 = f_getcurpl()
    test_equality(
        "f_wwrite",
        [f_dwread_epd(EPD(a)), f_dwread_epd(EPD(a) + 1), cp0, cp1, cp2],
        [0xDD03AABB, 0x080706CC, 0, 0, 0],
    )


@TestInstance
def test_ptr_constmemio():
    DoActions(
        SetMemory(0x656EB0, SetTo, 0x04030201),
        SetMemory(0x656EB4, SetTo, 0x08070605),
    )
    a = 0x656EB0

    # bread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    br0 = f_bread(a + 0)
    cp1 = f_getcurpl()
    br1 = f_bread(a + 3)
    cp2 = f_getcurpl()
    test_equality("f_bread(constexpr)", [cp0, br0, cp1, br1, cp2], [0, 1, 0, 4, 0])

    # wread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    wr0 = f_wread(a + 0)
    cp1 = f_getcurpl()
    wr1 = f_wread(a + 1)
    cp2 = f_getcurpl()
    wr2 = f_wread(a + 3)
    cp3 = f_getcurpl()
    test_equality(
        "f_wread(constexpr)",
        [cp0, wr0, cp1, wr1, cp2, wr2, cp3],
        [0, 0x0201, 0, 0x0302, 0, 0x0504, 0],
    )

    # dwread
    f_setcurpl(Player1)
    cp0 = f_getcurpl()
    dwr0 = f_dwread(a + 0)
    cp1 = f_getcurpl()
    dwr1 = f_dwread(a + 1)
    cp2 = f_getcurpl()
    dwr2 = f_dwread(a + 3)
    cp3 = f_getcurpl()
    test_equality(
        "f_dwread(constexpr)",
        [cp0, dwr0, cp1, dwr1, cp2, dwr2, cp3],
        [0, 0x04030201, 0, 0x05040302, 0, 0x07060504, 0],
    )

    DoActions(
        SetMemory(0x656EB0, SetTo, 0x04030201),
        SetMemory(0x656EB4, SetTo, 0x08070605),
    )
    # bwrite
    f_setcurpl(Player1)
    a = 0x656EB0
    cp0 = f_getcurpl()
    f_bwrite(a + 0, 5)
    cp1 = f_getcurpl()
    f_bwrite(a + 3, 7)
    cp2 = f_getcurpl()
    test_equality(
        "f_bwrite(constexpr)",
        [f_dwread_epd(EPD(a)), f_dwread_epd(EPD(a) + 1), cp0, cp1, cp2],
        [0x07030205, 0x08070605, 0, 0, 0],
    )

    # wwrite
    f_setcurpl(Player1)
    DoActions(
        SetMemory(0x656EB0, SetTo, 0x04030201),
        SetMemory(0x656EB4, SetTo, 0x08070605),
    )
    a = 0x656EB0
    cp0 = f_getcurpl()
    f_wwrite(a + 0, 0xAABB)
    cp1 = f_getcurpl()
    f_wwrite(a + 3, 0xCCDD)
    cp2 = f_getcurpl()
    test_equality(
        "f_wwrite(constexpr)",
        [f_dwread_epd(EPD(a)), f_dwread_epd(EPD(a) + 1), cp0, cp1, cp2],
        [0xDD03AABB, 0x080706CC, 0, 0, 0],
    )
