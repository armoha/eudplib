# Test added by zzt (Defender)

from helper import *  # noqa: F403


@TestInstance
def test_scdataobject():
    # FIXME
    # with expect_eperror():
    #     TrgUnit(233)
    marine = TrgUnit("Terran Marine")
    # with expect_eperror():
    #     TrgUnit(marine)
    marine = TrgUnit.cast(marine)
    test_equality("TrgUnit(marine) = 0", marine, 0)
    # test_equality("marine.maxHp = 40 * 256", marine.maxHp, 40 * 256)
    # test_equality(
    #     "marine.maxHp = EUDVar(40 * 256)", marine.maxHp, EUDVariable(40 * 256)
    # )

    test_equality("UnitData, check conversion to int", UnitData(13), 13)
    test_equality("marine.maxHp = 40 * 256", UnitData(0).maxHp, 40 * 256)
    test_equality(
        "marine.maxHp = EUDVar(40 * 256)", UnitData(0).maxHp, EUDVariable(40 * 256)
    )

    one = EUDVariable(1)
    ghost = UnitData(one)
    test_equality(
        "UnitData(EUDVar(ghost)).maxHp = EUDVar(45 * 256)",
        ghost.maxHp,
        EUDVariable(45 * 256),
    )

    ghost_cast = UnitData.cast(one)
    one << 2
    test_equality(
        "UnitData (variable) Max HP, check robustness to variable change",
        ghost.maxHp,
        EUDVariable(45 * 256),
    )
    test_equality(
        "UnitData (variable) Max HP, referencing variable",
        ghost_cast.maxHp,
        EUDVariable(80 * 256),
    )

    test_equality("arithmetic on UnitData", ghost + 3, 4)
    # with expect_eperror():
    ghost -= 1  # FIXME: should raise error?

    zealot_data = UnitData("Protoss Zealot")

    previous_value = zealot_data.maxHp
    zealot_data.maxHp = 80 * 256

    test_equality(
        "UnitData Max HP, check if read/write points to the same address",
        zealot_data.maxHp,
        80 * 256,
    )

    test_equality(
        "UnitData Max HP, check if write writes to the correct address",
        zealot_data.maxHp,
        f_dwread(0x662350 + 4 * EncodeUnit("Protoss Zealot")),
    )

    zealot_data.maxHp = previous_value

    previous_value = UnitData("Goliath Turret").maxHp
    UnitData("Goliath Turret").maxHp = 512

    test_equality(
        "UnitData Subunit, check UnitData to int conversion",
        UnitData("Terran Goliath").subUnit,
        EncodeUnit("Goliath Turret"),
    )

    test_equality(
        "UnitData Subunit, check if member type of unit works",
        UnitData("Terran Goliath").subUnit.maxHp,
        512,
    )

    test_equality(
        "UnitData Subunit, check if chain works",
        UnitData("Terran Goliath").subUnit.subUnit,
        228,
    )

    test_equality(
        "UnitData, check if chain through other data types works",
        UnitData("Protoss Dragoon").flingy,
        EncodeFlingy("Dragoon"),
    )

    test_equality(
        "UnitData, check if chain through other data types works",
        UnitData("Zerg Zergling").flingy.sprite,
        EncodeSprite("Zergling"),
    )

    test_equality(
        "UnitData, check if chain through other data types works",
        UnitData("Terran Marine").flingy.sprite.image,
        EncodeImage("Marine"),
    )

    archon_variable = EUDVariable()
    archon_variable << EncodeUnit("Protoss Archon")
    archon = UnitData(archon_variable)

    test_equality(
        "UnitData, check if chain from variable works",
        archon.flingy,
        EncodeFlingy("Archon Energy"),
    )

    test_equality(
        "UnitData, check if chain from variable works",
        archon.flingy.sprite,
        EncodeSprite("Archon Energy"),
    )

    test_equality(
        "UnitData, check if chain from variable works",
        archon.flingy.sprite.image,
        EncodeImage("Archon Energy"),
    )

    UnitData("Goliath Turret").maxHp = previous_value

    DoActions(SetResources(P7, SetTo, 100, OreAndGas))

    test_equality("PlayerData, check ore amount read", PlayerData(P7).mineral, 100)
    test_equality("PlayerData, check gas amount read", PlayerData(P7).gas, 100)

    PlayerData(P7).mineral += 200

    test_equality("PlayerData, check ore amount write", PlayerData(P7).mineral, 300)
    test_assert(
        "PlayerData, check ore amount write", Accumulate(P7, Exactly, 300, Ore)
    )

    DoActions(SetResources(P7, SetTo, 0, OreAndGas))

    with expect_eperror():
        UnitData("Artanis, GOD OF EUD")


@TestInstance
def test_epdoffsetmap_scdataobject_reference():
    goliath_cunit = CUnit.from_next()
    DoActions(CreateUnit(1, "Terran Goliath", "Anywhere", P8))
    test_equality(
        "Cunit subunit type check",
        goliath_cunit.subUnit.unitType,
        UnitData("Goliath Turret"),
    )

    DoActions(RemoveUnit("Terran Goliath", P8))
