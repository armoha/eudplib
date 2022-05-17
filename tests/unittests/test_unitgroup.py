from helper import *


@TestInstance
def test_unitgroup():
    g = UnitGroup(1000, CurrentPlayer)
    g.add(3)
    g.add(EUDVariable(2))
    g.add(EUDVariable(6))

    k = EUDArray(7)
    for unit in g:  # 22, 21, 25
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
    for unit in g:
        f_dwadd_epd(EPD(0x6509B0), EPD(m))
        for dead in unit.dying:
            f_dwwrite_cp(0, 3)
            dead.move_cp(0)
            f_dwwrite_cp(0, 1)
        unit.move_cp(0)  # unit and dead are same object
        f_dwwrite_cp(0, 2)  # Never happen
    indexes = (0, 2, 3, 4, 6)
    result = [1 if i in indexes else 3 if (i - 19) in indexes else 0 for i in range(26)]
    test_equality("UnitGroup dying test", [m[i] for i in range(26)], result)
