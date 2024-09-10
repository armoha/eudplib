# Test added by zzt (Defender)

from helper import *  # noqa: F403


@TestInstance
def test_scdata():
    # FIXME
    # with expect_eperror():
    #     TrgUnit(233)
    marine = TrgUnit("Terran Marine")
    marine = TrgUnit(marine)  # copy inner value
    marine = TrgUnit.cast(marine)  # share reference
    test_equality("TrgUnit(marine) = 0", marine, 0)
    test_equality("marine.maxHp = 40 * 256", marine.maxHp, 40 * 256)
    test_equality(
        "marine.maxHp = EUDVar(40 * 256)", marine.maxHp, EUDVariable(40 * 256)
    )

    one = EUDVariable(1)
    trigcount = GetTriggerCounter()
    ghost = TrgUnit(one)  # copy variable one
    ep_assert(
        trigcount + 1 == GetTriggerCounter(),
        f"Trigger count mismatch: {trigcount} + 1 != {GetTriggerCounter()}",
    )
    test_equality(
        "TrgUnit(EUDVar(ghost)).maxHp = EUDVar(45 * 256)",
        ghost.maxHp,
        EUDVariable(45 * 256),
    )

    trigcount = GetTriggerCounter()
    ghost_cast = TrgUnit.cast(one)  # reuse variable
    ep_assert(
        trigcount == GetTriggerCounter(),
        f"Trigger count mismatch: {trigcount} != {GetTriggerCounter()}",
    )
    ep_assert(one is not ghost._value)
    ep_assert(one is ghost_cast._value)
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
    ghost << 2
    ep_assert(isinstance(ghost, TrgUnit), "preserve type on assignment")
    test_equality(
        "TrgUnit(eudvar).maxHp, after assignment",
        ghost_cast.maxHp,
        EUDVariable(80 * 256),
    )
    ghost -= 1
    ep_assert(not isinstance(ghost, TrgUnit), "losing type on in-place operations")

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

    test_equality(
        "TrgPlayer.ore, check ore, gas amounts read", [P7.ore, P7.gas], [100, 100]
    )

    P7.ore += 200

    test_equality("TrgPlayer.ore, check ore amount write", P7.ore, 300)
    test_assert("TrgPlayer.ore, check Accumulate", Accumulate(P7, Exactly, 300, Ore))
    DoActions(SetResources(P7, SetTo, 0, OreAndGas))

    with expect_eperror():
        TrgUnit("zzt, GOD OF EUD")

    scv = TrgUnit("Terran SCV")
    test_equality("scv.baseProperty flags", scv.baseProperty, 0x58010008)
    scv.baseProperty.Hero = True
    test_equality(
        "scv.baseProperty individual flags",
        [
            scv.baseProperty.Worker,
            scv.baseProperty.AutoAttackAndMove,
            scv.baseProperty.CanAttack,
            scv.baseProperty.Mechanical,
            scv.baseProperty.Hero,
            scv.baseProperty.ResourceDepot,
        ],
        [
            True,
            True,
            True,
            True,
            True,
            False,
        ],
    )

    test_equality("scv.nameString == 0", scv.nameString, 0)
    name = EncodeString("dpdkfah!")  # EncodeString does string interning
    scv.nameString = "dpdkfah!"
    test_equality("scv.nameString test", scv.nameString, name)
    # FIXME
    # with expect_eperror():
    #     scv.nameString = 65536

    test_equality(
        "scv.dontBecomeGuard == True",
        scv.dontBecomeGuard,
        True,
    )
    scv.dontBecomeGuard = False
    test_equality(
        "scv.dontBecomeGuard == False",
        scv.dontBecomeGuard,
        False,
    )
    with expect_error(NotImplementedError):
        scv.iaddattr("dontBecomeGuard", 1)

    P1.unitColor = 123
    test_equality("P1.unitColor = 123", P1.unitColor, 123)
    test_equality("P1.unitColor", P1.unitColor, f_bread(0x581D76))
    P2.unitColor = 234
    test_equality("P2.unitColor = 234", P2.unitColor, 234)


@TestInstance  # noqa: F405
def test_scdata_reference():
    goliath_cunit = CUnit.from_next()
    DoActions(CreateUnit(1, "Terran Goliath", "Anywhere", P8))
    test_equality(
        "Cunit subunit type check",
        goliath_cunit.subUnit.unitType,
        TrgUnit("Goliath Turret"),
    )

    DoActions(RemoveUnit("Terran Goliath", P8))


@TestInstance  # noqa: F405
def test_scdata_caching():
    ptr = EUDVariable()

    @EUDFunc
    def foo():
        return CUnit.from_ptr(ptr)

    test_equality("caching skip test", foo(), 0)

    epds = []
    ptr << 0x58A364 + 4
    epds.append(foo())

    ptr << 0x58A364
    epds.append(foo())

    ptr << 0x58A364 + 8
    epds.append(foo())

    ptr << 0
    epds.append(foo())
    test_equality("caching tests", epds, [1, 0, 2, 0])
