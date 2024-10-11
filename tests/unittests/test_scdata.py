# Test added by zzt (Defender)
from random import randint

from helper import *


@TestInstance
def test_scdata():
    # FIXME
    # with expect_eperror():
    #     TrgUnit(233)
    TrgUnit("Terran Vulture").groundWeapon.damage += 3
    marine = TrgUnit("Terran Marine")
    marine = TrgUnit(marine)  # copy inner value
    marine = TrgUnit.cast(marine)  # share reference
    test_equality("TrgUnit(marine) = 0", marine, 0)
    test_equality("marine.maxHp = 40 * 256", marine.maxHp, 40 * 256)
    test_equality(
        "marine.maxHp = EUDVar(40 * 256)", marine.maxHp, EUDVariable(40 * 256)
    )
    test_assert("marine.maxHp = 40 * 256 conditional", marine.maxHp == 40 * 256)

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
    test_assert(
        "TrgUnit(EUDVar(ghost)).maxHp = EUDVar(45 * 256) conditional",
        ghost.maxHp == 45 * 256,
    )

    trigcount = GetTriggerCounter()
    ghost_cast = TrgUnit.cast(one)  # reuse variable
    ep_assert(
        trigcount == GetTriggerCounter(),
        f"Trigger count mismatch: {trigcount} != {GetTriggerCounter()}",
    )
    ep_assert(one is not ghost._value, "New instance should not alias")
    ep_assert(one is ghost_cast._value, "cast should alias")
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
    test_assert(
        "TrgUnit(eudvar).maxHp conditional",
        ghost_cast.maxHp == 80 * 256,
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
    ep_assert(isinstance(ghost, TrgUnit), "preserve type after in-place operations")

    zealot_data = TrgUnit("Protoss Zealot")

    previous_value = zealot_data.maxHp
    zealot_data.maxHp = 80 * 256

    test_equality(
        "TrgUnit.maxHp, check if read/write points to the same address",
        zealot_data.maxHp,
        80 * 256,
    )

    test_equality(
        "TrgUnit.maxHp, check if write writes to the correct address",
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
    test_assert(
        "TrgUnit.subUnit conditional",
        TrgUnit("Terran Goliath").subUnit == TrgUnit("Goliath Turret"),
    )
    test_equality(
        "TrgUnit.subUnit, check if member type of unit works",
        TrgUnit("Terran Goliath").subUnit.maxHp,
        512,
    )
    test_assert(
        "TrgUnit.subUnit.maxHp conditional",
        TrgUnit("Terran Goliath").subUnit.maxHp == 512,
    )

    test_equality(
        "TrgUnit.subUnit, check if chain works",
        TrgUnit("Terran Goliath").subUnit.subUnit,
        228,
    )
    test_assert(
        "TrgUnit.subUnit.subUnit conditional",
        TrgUnit("Terran Goliath").subUnit.subUnit == 228,
    )

    test_equality(
        "TrgUnit.flingy, check if chain through other data types works",
        TrgUnit("Protoss Dragoon").flingy,
        Flingy("Dragoon"),
    )
    test_assert(
        "TrgUnit.flingy conditional",
        TrgUnit("Protoss Dragoon").flingy == Flingy("Dragoon"),
    )

    test_equality(
        "TrgUnit.flingy.sprite, check if chain through other data types works",
        TrgUnit("Zerg Zergling").flingy.sprite,
        Sprite("Zergling"),
    )
    test_assert(
        "TrgUnit.flingy.sprite conditional",
        TrgUnit("Zerg Zergling").flingy.sprite == Sprite("Zergling"),
    )

    test_equality(
        "TrgUnit.flingy.sprite.image, check if chain through other data types works",
        TrgUnit("Terran Marine").flingy.sprite.image,
        Image("Marine"),
    )
    test_assert(
        "TrgUnit.flingy.sprite.image conditional",
        TrgUnit("Terran Marine").flingy.sprite.image == Image("Marine"),
    )

    archon_variable = EUDVariable()
    archon_variable << TrgUnit("Protoss Archon")
    archon = TrgUnit(archon_variable)

    test_equality(
        "TrgUnit.flingy, check if chain from variable works",
        archon.flingy,
        Flingy("Archon Energy"),
    )
    test_assert(
        "TrgUnit.flingy conditional", archon.flingy == Flingy("Archon Energy")
    )

    test_equality(
        "TrgUnit.flingy.sprite, check if chain from variable works",
        archon.flingy.sprite,
        Sprite("Archon Energy"),
    )
    test_assert(
        "TrgUnit.flingy.sprite conditional",
        archon.flingy.sprite == Sprite("Archon Energy"),
    )

    test_equality(
        "TrgUnit.flingy.sprite.image, check if chain from variable works",
        archon.flingy.sprite.image,
        Image("Archon Energy"),
    )
    test_assert(
        "TrgUnit.flingy.sprite.image conditional",
        archon.flingy.sprite.image == Image("Archon Energy"),
    )

    TrgUnit("Goliath Turret").maxHp = previous_value
    DoActions(SetResources(P7, SetTo, 100, OreAndGas))

    test_equality(
        "TrgPlayer.ore, check ore, gas amounts read", [P7.ore, P7.gas], [100, 100]
    )
    test_assert(
        "TrgPlayer.ore/gas conditional",
        [P7.ore == 100, P7.gas == 100],
    )

    P7.ore += 200

    test_equality("TrgPlayer.ore, check ore amount write", P7.ore, 300)
    test_assert("TrgPlayer.ore, check Accumulate", Accumulate(P7, Exactly, 300, Ore))
    DoActions(SetResources(P7, SetTo, 0, OreAndGas))

    with expect_eperror():
        TrgUnit("zzt, GOD OF EUD")

    scv = TrgUnit("Terran SCV")
    test_equality("scv.baseProperty flags", scv.baseProperty, 0x58010008)
    test_assert("scv.baseProperty flags conditional", scv.baseProperty == 0x58010008)

    temp = scv.baseProperty
    temp.Building = False
    ep_assert(type(temp._value_lazy) is Forward)
    _flag = temp.Building
    ep_assert(type(temp._value_lazy) is EUDVariable)
    scv.baseProperty = temp

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
    test_assert(
        "scv.baseProperty individual flags conditional",
        [
            scv.baseProperty.Worker == True,
            scv.baseProperty.AutoAttackAndMove == True,
            scv.baseProperty.CanAttack == True,
            scv.baseProperty.Mechanical == True,
            scv.baseProperty.Hero == True,
            scv.baseProperty.ResourceDepot == False,
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
    test_assert("P1.unitColor = 123 conditional", P1.unitColor == 123)
    test_equality("P1.unitColor", P1.unitColor, f_bread(0x581D76))
    P2.unitColor = 234
    test_equality("P2.unitColor = 234", P2.unitColor, 234)

    P1.unitColor = 111
    P2.unitColor = 165


@TestInstance
def test_scdata_reference():
    goliath_cunit = CUnit.from_next()
    DoActions(CreateUnit(1, "Terran Goliath", "Anywhere", P8))
    test_equality(
        "Cunit subunit type check",
        goliath_cunit.subUnit.unitType,
        TrgUnit("Goliath Turret"),
    )

    DoActions(RemoveUnit("Terran Goliath", P8))


@TestInstance
def test_scdata_caching():
    from eudplib.memio import muldiv4table
    from eudplib.scdata.offsetmap import EPDOffsetMap

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

    p = TrgPlayer.cast(EUDVariable())
    v = p._value
    p << P8
    P8.minimapColor = 128
    color = p.minimapColor
    update_start, update_restore, update_end = EPDOffsetMap._update[v]
    test_equality("P8.minimapColor = 128", color, 128)
    test_equality("Cache invalidation", f_dwread(update_start + 4), update_restore)

    P8.unitColor = 178
    test_equality("P8.unitColor = 178", p.unitColor, 178)
    test_equality(
        "Reuse cached values",
        f_dwread(update_start + 4),
        f_dwread(update_start + 348),
    )

    u = TrgUnit.cast(v)
    u << "Alan Schezar"
    test_equality("Alan Schezar.timeCost", u.timeCost, 1200)
    test_equality("Cache invalidation", f_dwread(update_start + 4), update_restore)
    test_equality(
        "varcount", EUDVariable(update_end), muldiv4table.muldiv_end_table[5]
    )

    # += 1 is specialized to update cached values
    u += 1
    f_simpleprint("VAL:", u, ", CACHE_COND:", f_dwread(update_start + 16))
    test_equality("Alan Schezar += 1; .flingy", u.flingy, Flingy("Goliath Turret"))
    test_equality(
        "Reuse cached values",
        f_dwread(update_start + 4),
        f_dwread(update_start + 348),
    )

    P8.unitColor = 135
    P8.minimapColor = 135


@TestInstance
def test_scdata_value_range_extension():
    v = EUDVariable(0x17)  # 23

    p = TrgPlayer.cast(v)
    P12.cumulativeMineral = 9999  # 0x57F1AC = 0x57F150 + 0x17 * 4
    test_equality("TrgPlayer with bitmask 0xFF", p.cumulativeGas, 9999)

    u = TrgUnit.cast(v)
    # TrgUnit usage will extend bitmask of `v` from 0xF to 0xFF
    # and this applies retroactively to every usages of `v`
    test_equality("TrgUnit with bitmask 0xFF", u.gasCost, 200)

    P12.cumulativeMineral = 0


@TestInstance
def test_scdata_var():
    p = TrgPlayer.cast(EUDVariable(4))
    test_equality("P5 Color = 156", [p.minimapColor, p.unitColor], [156, 156])
    p += 1
    test_equality("P6 Color = 19", [p.minimapColor, p.unitColor], [19, 19])
    p += 1
    test_equality("P7 Color = 84", [p.minimapColor, p.unitColor], [84, 84])
    p += 1
    test_equality("P8 Color = 135", [p.minimapColor, p.unitColor], [135, 135])
    p += 1
    test_equality("P9 Color = 185", [p.minimapColor, p.unitColor], [185, 185])


@TestInstance
def test_scdata_current_upgrade():
    for upgrade_id in (Upgrade("Protoss Plasma Shields"), Upgrade("Charon Booster")):
        upgrades = [Upgrade(upgrade_id), Upgrade(EUDVariable(upgrade_id))]
        players = [P11, TrgPlayer(EUDVariable(10))]
        if upgrade_id < 46:
            ptr = 0x58D2B0 + upgrade_id + 46 * 10
        else:
            ptr = 0x58F32C + upgrade_id - 46 + 15 * 10
        for upgrade, player in zip(upgrades, players):
            lv = randint(1, 255)
            u = "var" if IsEUDVariable(upgrade) else "const"
            p = "var" if IsEUDVariable(player) else "const"
            f_bwrite(ptr, lv)
            test_equality(f"lv = Upgrade({u})[TrgPlayer({p})]", upgrade[player], lv)

            lv = randint(1, 255)
            upgrade[player] = lv
            test_equality(f"Upgrade({u})[TrgPlayer({p})] = lv", f_bread(ptr), lv)

        f_bwrite(ptr, 0)

    for tech_id in (Tech("Burrowing"), Tech("Feedback")):
        techs = [Tech(tech_id), Tech(EUDVariable(tech_id))]
        players = [P12, TrgPlayer(EUDVariable(11))]
        if tech_id < 24:
            ptr = 0x58CF44 + tech_id + 24 * 11
        else:
            ptr = 0x58F140 + tech_id - 24 + 20 * 11
        for tech, player in zip(techs, players):
            lv = 1
            u = "var" if IsEUDVariable(tech) else "const"
            p = "var" if IsEUDVariable(player) else "const"
            f_bwrite(ptr, lv)
            test_equality(f"lv = Tech({u})[TrgPlayer({p})]", tech[player], lv)

            lv = 0
            tech[player] = lv
            test_equality(f"Tech({u})[TrgPlayer({p})] = lv", f_bread(ptr), lv)
