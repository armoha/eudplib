# Test added by zzt (Defender)

from helper import *  # noqa: F403


@TestInstance
def test_scdataobject():
    test_equality("UnitData Max HP, compare against const", UnitData(0).maxHP, 40 * 256)

    forty_times_256 = EUDVariable()
    forty_times_256 << 40 * 256
    test_equality("UnitData Max HP, compare against variable",
                  UnitData(0).maxHP, forty_times_256)

    one = EUDVariable()
    one << 1
    fortyfive_times_256 = EUDVariable()
    fortyfive_times_256 << 45 * 256

    ghost_data = UnitData(one)

    test_equality("UnitData (variable) Max HP, compare against variable",
                  ghost_data.maxHP, fortyfive_times_256)

    # one << 2

    # test_equality("UnitData (variable) Max HP, check robustness to variable change",
    #               ghost_data.maxHP, fortyfive_times_256)

    ghost_data + 3 # shouldn't raise error, but not an intended use case
    ghost_data -= 1 # also shouldn't raise error, not an intended use case either

    zealot_data = UnitData("Protoss Zealot")

    zealot_data.maxHP = 80 * 256

    test_equality("UnitData Max HP, check if read/write points to the same address",
                  zealot_data.maxHP, 80 * 256)

    test_equality("UnitData Max HP, check if write writes to the correct address",
                  zealot_data.maxHP,
                  f_dwread(0x662350 + 4 * EncodeUnit("Protoss Zealot")))

