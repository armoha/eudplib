from helper import *


@TestInstance
def test_unitloop():
    for ptr, epd in EUDLoopUnit2():
        pass


@TestInstance
def test_unitgroup():
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
        f_dwadd_epd(EPD(0x6509B0), EPD(k) - 19)
        f_dwwrite_cp(0, 1)
    test_equality("Basic UnitGroup test", [k[i] for i in range(7)], [0, 0, 1, 1, 0, 0, 1])

    g.add(4)
    g.add(EUDVariable(0))
    m = EUDArray(7 + 19)
    for unit in g.cploop:
        f_dwadd_epd(EPD(0x6509B0), EPD(m))
        for dead in unit.dying:
            f_dwwrite_cp(0, 3)
            dead.move_cp(0)
            f_dwwrite_cp(0, 1)
        unit.move_cp(0)  # unit and dead are same object
        f_dwwrite_cp(0, 2)  # Never happen

    for unit in g.cploop:
        # NEVER run since all units were already removed from group 'g'
        f_dwadd_epd(EPD(0x6509B0), EPD(m))
        f_dwwrite_cp(0, 2)
        unit.move_cp(0)
        f_dwwrite_cp(0, 2)
        unit.remove()  # this call is mandatory.
    indexes = (0, 2, 3, 4, 6)
    result = [1 if i in indexes else 3 if (i - 19) in indexes else 0 for i in range(26)]
    test_equality("UnitGroup dying test", [m[i] for i in range(26)], result)

    # test mandatory remove call
    if EUDIf()(False):
        ug = UnitGroup(3)
        ug.add(7)
        try:
            for unit in ug.cploop:
                pass
        except EPError:
            unit.remove()
        else:
            raise EPError("unit.remove() call is mandatory")
    EUDEndIf()

    for ptr, epd in EUDLoopNewUnit():
        pass
