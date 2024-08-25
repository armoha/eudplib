from helper import *


@TestInstance
def test_dwpatch():
    from eudplib.eudlib.utilf.mempatch import (
        f_dwpatch_epd,
        f_blockpatch_epd,
        f_unpatchall,
    )

    # Initial value
    DoActions(SetMemory(0x58A364, SetTo, 1234), SetMemory(0x58A368, SetTo, 5678))

    # f_dwpatch
    f_dwpatch_epd(EPD(0x58A364), 123)
    f_dwpatch_epd(EPD(0x58A368), 456)
    test_assert(
        "f_dwpatch test",
        [f_dwread_epd(EPD(0x58A364)) == 123, f_dwread_epd(EPD(0x58A368)) == 456],
    )

    # f_blockpatch
    data = Db(b"\x01\x02\x03\x04\x05\x06\x07\x08")
    f_blockpatch_epd(EPD(0x58A364), EPD(data), 2)
    test_assert(
        "f_blockpatch_epd test",
        [
            f_dwread_epd(EPD(0x58A364)) == 0x04030201,
            f_dwread_epd(EPD(0x58A368)) == 0x08070605,
        ],
    )

    # unpatch
    f_unpatchall()
    test_assert(
        "f_unpatchall test (Relies on patches above)",
        [f_dwread_epd(EPD(0x58A364)) == 1234, f_dwread_epd(EPD(0x58A368)) == 5678],
    )

    # reset
    DoActions(SetMemory(0x58A364, SetTo, 0), SetMemory(0x58A368, SetTo, 0))
