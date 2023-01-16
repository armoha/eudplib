from helper import *
from eudplib.offsetmap import EPDOffsetMap, Member, MemberKind


class T(EPDOffsetMap):
    a = Member(0x00, MemberKind.DWORD)
    b = Member(0x00, MemberKind.WORD)
    c = Member(0x02, MemberKind.WORD)
    d = Member(0x04, MemberKind.DWORD)
    e = Member(0x07, MemberKind.BYTE)


@TestInstance
def test_ctypes():
    a = Db(b"\x00\x01\x02\x03\x04\x05\x06\x07")
    # FIXME: with expect_typeerror():
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
