# Test added by zzt (Defender)

from helper import *  # noqa: F403


@TestInstance
def test_scdata():
    # FIXME
    # with expect_eperror():
    #     TrgUnit(233)
    marine = TrgUnit("Terran Marine")
    # with expect_eperror():
    #     TrgUnit(marine)
    marine = TrgUnit.cast(marine)
    test_equality("TrgUnit(marine) = 0", marine, EUDVariable(0))
    test_equality("marine.maxHp = 40 * 256", marine.maxHp, 40 * 256)
    test_equality(
        "marine.maxHp = EUDVar(40 * 256)", marine.maxHp, EUDVariable(40 * 256)
    )

    one = EUDVariable(1)
    ghost = TrgUnit(one)
    test_equality(
        "TrgUnit(EUDVar(ghost)).maxHp = EUDVar(45 * 256)",
        ghost.maxHp,
        EUDVariable(45 * 256),
    )

    ghost_cast = TrgUnit.cast(one)
    ep_assert(one is not ghost._value and one is ghost_cast._value)
    one << 2
    test_equality(
        "TrgUnit(eudvar).maxHp, check robustness to variable change",
        ghost.maxHp,
        EUDVariable(45 * 256),
    )
    test_equality(
        "TrgUnit(eudvar).maxHp, referencing variable",
        ghost_cast.maxHp,
        EUDVariable(80 * 256),
    )

    test_equality("arithmetic on UnitData", ghost + 3, 4)
    # with expect_eperror():
    ghost -= 1  # FIXME: should raise error?

    zealot_data = TrgUnit("Protoss Zealot")

    previous_value = zealot_data.maxHp
    zealot_data.maxHp = 80 * 256

    test_equality(
        "TrgUnit.maxHp, check if read/write points to the same address",
        zealot_data.maxHp,
        80 * 256,
    )

    test_equality(
        "TrgUnit.maxH, check if write writes to the correct address",
        zealot_data.maxHp,
        f_dwread(0x662350 + 4 * TrgUnit("Protoss Zealot")),
    )

    zealot_data.maxHp = previous_value

    previous_value = TrgUnit("Goliath Turret").maxHp
    TrgUnit("Goliath Turret").maxHp = 512

    test_equality(
        "TrgUnit.subUnit, check UnitData to int conversion",
        TrgUnit("Terran Goliath").subUnit,
        TrgUnit("Goliath Turret"),
    )
    test_equality(
        "TrgUnit.subUnit, check if member type of unit works",
        TrgUnit("Terran Goliath").subUnit.maxHp,
        512,
    )

    test_equality(
        "TrgUnit.subUnit, check if chain works",
        TrgUnit("Terran Goliath").subUnit.subUnit,
        228,
    )

    test_equality(
        "TrgUnit.flingy, check if chain through other data types works",
        TrgUnit("Protoss Dragoon").flingy,
        Flingy("Dragoon"),
    )

    test_equality(
        "TrgUnit.flingy.sprite, check if chain through other data types works",
        TrgUnit("Zerg Zergling").flingy.sprite,
        Sprite("Zergling"),
    )

    test_equality(
        "TrgUnit.flingy.sprite.image, check if chain through other data types works",
        TrgUnit("Terran Marine").flingy.sprite.image,
        Image("Marine"),
    )

    archon_variable = EUDVariable()
    archon_variable << TrgUnit("Protoss Archon")
    archon = TrgUnit(archon_variable)

    test_equality(
        "TrgUnit.flingy, check if chain from variable works",
        archon.flingy,
        Flingy("Archon Energy"),
    )

    test_equality(
        "TrgUnit.flingy.sprite, check if chain from variable works",
        archon.flingy.sprite,
        Sprite("Archon Energy"),
    )

    test_equality(
        "TrgUnit.flingy.sprite.image, check if chain from variable works",
        archon.flingy.sprite.image,
        Image("Archon Energy"),
    )

    TrgUnit("Goliath Turret").maxHp = previous_value
    DoActions(SetResources(P7, SetTo, 100, OreAndGas))

    test_equality("TrgPlayer.ore, check ore amount read", P7.ore, 100)
    test_equality("TrgPlayer.gas, check gas amount read", P7.gas, 100)

    P7.ore += 200

    test_equality("TrgPlayer.ore, check ore amount write", P7.ore, 300)
    test_assert("TrgPlayer.ore, check Accumulate", Accumulate(P7, Exactly, 300, Ore))
    DoActions(SetResources(P7, SetTo, 0, OreAndGas))

    with expect_eperror():
        TrgUnit("zzt, GOD OF EUD")


@TestInstance
def test_epdoffsetmap_scdataobject_reference():
    goliath_cunit = CUnit.from_next()
    DoActions(CreateUnit(1, "Terran Goliath", "Anywhere", P8))
    test_equality(
        "Cunit subunit type check",
        goliath_cunit.subUnit.unitType,
        TrgUnit("Goliath Turret"),
    )

    DoActions(RemoveUnit("Terran Goliath", P8))