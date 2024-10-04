from helper import *

from eudplib.scdata.offsetmap import (
    ByteMember,
    DwordMember,
    EPDOffsetMap,
    WordMember,
)


class T(EPDOffsetMap):
    a = DwordMember("struct", 0x00)
    b = WordMember("struct", 0x00)
    c = WordMember("struct", 0x02)
    d = DwordMember("struct", 0x04)
    e = ByteMember("struct", 0x07)


@TestInstance
def test_ctypes():
    a = Db(b"\x00\x01\x02\x03\x04\x05\x06\x07")
    # FIXME: with expect_error(TypeError):
    t = T(a)
    t = T(EUDVariable(EPD(a)))
    test_equality(
        "Reading from EPDOffsetMap",
        [t.a, t.b, t.c, t.d, t.e],
        [0x03020100, 0x0100, 0x0302, 0x07060504, 0x07],
    )

    t.a = 0x0D0C0B0A
    t.c = 0x0302
    t.e = 0x11

    test_equality(
        "Writing to EPDOffsetMap",
        [f_dwread_epd(EPD(a) + 0), f_dwread_epd(EPD(a) + 1)],
        [0x03020B0A, 0x11060504],
    )
