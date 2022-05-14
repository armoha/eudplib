from helper import *


@TestInstance
def test_ctypes():
    t = EPDOffsetMap(
        {
            "a": (4, 0x0000),
            "b": (2, 0x0000),
            "c": (2, 0x0002),
            "d": (4, 0x0004),
            "e": (1, 0x0007),
        }
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
        [0x03020B0A, 0x11060504],
    )

    ptr, epd = f_cunitepdread_epd(EPD(0x628438))
    f_setloc("Anywhere", 0, 0)
    DoActions(
        CreateUnitWithProperties(
            1,
            "Protoss Scout",
            "Anywhere",
            P1,
            UnitProperty(invincible=True),
        ),
        CreateUnit(1, "Protoss Scout", "Anywhere", P1),
    )
    cunit = EPDCUnitMap(epd)
    test_equality(
        "cunit.unitId",
        [cunit.unitId],
        [EncodeUnit("Protoss Scout")],
    )
    test_assert("cunit.unitId == Scout", cunit.unitId == EncodeUnit("Artanis"))
    test_equality(
        "cunit.owner",
        [cunit.owner],
        [EncodePlayer(P1)],
    )
    test_assert("cunit.owner == P1", cunit.owner == EncodePlayer(P1))
    test_equality(
        "cunit.statusFlags",
        [cunit.statusFlags],
        [0xC4110005],
    )
    test_assert("cunit.check_status_flag", cunit.check_status_flag(0x4110005))
