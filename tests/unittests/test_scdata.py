# Test added by zzt (Defender)

from helper import *  # noqa: F403


@TestInstance
def test_scdataobject():
    test_equality("UnitData, check conversion to int",
                  UnitData(13), 13)
    previous_value = EUDVariable()

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

    one << 2

    test_equality("UnitData (variable) Max HP, check robustness to variable change",
                  ghost_data.maxHP, fortyfive_times_256)

    ghost_data + 3 # shouldn't raise error, but not an intended use case
    ghost_data -= 1 # also shouldn't raise error, not an intended use case either

    zealot_data = UnitData("Protoss Zealot")

    previous_value = zealot_data.maxHP
    zealot_data.maxHP = 80 * 256

    test_equality("UnitData Max HP, check if read/write points to the same address",
                  zealot_data.maxHP, 80 * 256)

    test_equality("UnitData Max HP, check if write writes to the correct address",
                  zealot_data.maxHP,
                  f_dwread(0x662350 + 4 * EncodeUnit("Protoss Zealot")))

    zealot_data.maxHP = previous_value

    previous_value = UnitData("Goliath Turret").maxHP
    UnitData("Goliath Turret").maxHP = 512

    test_equality("UnitData Subunit, check UnitData to int conversion",
                  UnitData("Terran Goliath").subUnit,
                  EncodeUnit("Goliath Turret"))

    test_equality("UnitData Subunit, check if member type of unit works",
                  UnitData("Terran Goliath").subUnit.maxHP, 512)

    test_equality("UnitData Subunit, check if chain works",
                  UnitData("Terran Goliath").subUnit.subUnit, 228)

    test_equality("UnitData, check if chain through other data types works",
                  UnitData("Protoss Dragoon").flingy,
                  EncodeFlingy("Dragoon"))

    test_equality("UnitData, check if chain through other data types works",
                  UnitData("Zerg Zergling").flingy.sprite,
                  EncodeSprite("Zergling"))

    test_equality("UnitData, check if chain through other data types works",
                  UnitData("Terran Marine").flingy.sprite.image,
                  EncodeImage("Marine"))

    archon_variable = EUDVariable()
    archon_variable << EncodeUnit("Protoss Archon")
    archon = UnitData(archon_variable)

    test_equality("UnitData, check if chain from variable works",
                  archon.flingy,
                  EncodeFlingy("Archon Energy"))

    test_equality("UnitData, check if chain from variable works",
                  archon.flingy.sprite,
                  EncodeSprite("Archon Energy"))

    test_equality("UnitData, check if chain from variable works",
                  archon.flingy.sprite.image,
                  EncodeImage("Archon Energy"))

    UnitData("Goliath Turret").maxHP = previous_value

    DoActions(SetResources(P7, SetTo, 100, OreAndGas))

    test_equality("PlayerData, check ore amount read",
                  PlayerData(P7).mineral, 100)
    test_equality("PlayerData, check gas amount read",
                  PlayerData(P7).gas, 100)

    PlayerData(P7).mineral += 200

    test_equality("PlayerData, check ore amount write",
                  PlayerData(P7).mineral, 300)
    test_assert("PlayerData, check ore amount write",
                Accumulate(P7, Exactly, 300, Ore))

    DoActions(SetResources(P7, SetTo, 0, OreAndGas))

    with expect_eperror():
        u = UnitData("Artanis, GOD OF EUD")


@TestInstance
def test_epdoffsetmap_scdataobject_reference():
    goliath_cunit = CUnit.from_next()
    DoActions(CreateUnit(1, "Terran Goliath", "Anywhere", P8))
    test_equality("Cunit subunit type check",
                  goliath_cunit.subUnit.unitType,
                  UnitData("Goliath Turret"))

    DoActions(RemoveUnit("Terran Goliath", P8))
