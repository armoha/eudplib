from helper import *


@TestInstance
def test_ctypes():
    t = EPDOffsetMap(
        (
            ("a", 0x0000, 4),
            ("b", 0x0000, 2),
            ("c", 0x0002, 2),
            ("d", 0x0004, 4),
            ("e", 0x0007, 1),
        )
    )

    a = Db(b"\x00\x01\x02\x03\x04\x05\x06\x07")
    a_ = t(a)
    a_ = t(EPD(a))
    test_equality(
        "Reading from EPDOffsetMap",
        [a_.a, a_.b, a_.c, a_.d, a_.e],
        [0x03020100, 0x0100, 0x0302, 0x07060504, 0x07],
    )

    a_.a = 0x0D0C0B0A
    a_.c = 0x0302
    a_.e = 0x11

    m = f_dwread_epd(EPD(a) + 0)
    n = f_dwread_epd(EPD(a) + 1)

    test_equality(
        "Writing to EPDOffsetMap",
        [f_dwread_epd(EPD(a) + 0), f_dwread_epd(EPD(a) + 1)],
        [0x03020B0A, 0x11060504]
    )
