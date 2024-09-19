from helper import *


@TestInstance
def test_unitloop():
    for ptr, epd in EUDLoopUnit2():
        pass


@TestInstance
def test_unitgroup():
    get_epd = lambda x: x if x._value._is_epd() else EPD(x)
    g = UnitGroup(1000)
    g.add(3)
    g.add(EUDVariable(2))
    g.add(EUDVariable(6))

    k = EUDArray(7)
    for unit in g.cploop:  # 22, 21, 25
        if EUDIf()(False):
            for dead in unit.dying:
                pass
        EUDEndIf()
        # NOTE: Should we guarantee that first offset is always 0x4C?
        unit.move_cp(0x4C // 4)  # NO-OP
        f_dwadd_epd(EPD(0x6509B0), get_epd(k) - 19)
        f_dwwrite_cp(0, 1)
    test_equality(
        "Basic UnitGroup test", [k[i] for i in range(7)], [0, 0, 1, 1, 0, 0, 1]
    )

    g.add(4)
    g.add(EUDVariable(0))
    m = EUDArray(7 + 19)
    for unit in g.cploop:
        f_dwadd_epd(EPD(0x6509B0), get_epd(m))
        for dead in unit.dying:
            f_dwwrite_cp(0, 3)
            dead.move_cp(0)
            f_dwwrite_cp(0, 1)
        unit.move_cp(0)  # unit and dead are same object
        f_dwwrite_cp(0, 2)  # Never happen

    for unit in g.cploop:
        # NEVER run since all units were already removed from group 'g'
        f_dwadd_epd(EPD(0x6509B0), get_epd(m))
        f_dwwrite_cp(0, 2)
        unit.move_cp(0)
        f_dwwrite_cp(0, 2)
        unit.remove()  # this call is mandatory.
    indexes = (0, 2, 3, 4, 6)
    result = [
        1 if i in indexes else 3 if (i - 19) in indexes else 0 for i in range(26)
    ]
    test_equality("UnitGroup dying test", [m[i] for i in range(26)], result)

    count = EUDVariable()
    DoActions(CreateUnit(12, "Zerg Broodling", 64, P8), count.SetNumber(0))
    for cunit in EUDLoopPlayerCUnit(P8):
        count += 1
        Trigger(cunit.eqattr("unitType", "Zerg Broodling"), count.AddNumber(100))
    test_equality("EUDLoopPlayerCUnit test", count, 1212)
