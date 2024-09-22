from helper import *


@TestInstance
def test_operator_lvalue():
    a, b = EUDVariable(), EUDVariable()
    with expect_eperror():
        (a + b) << 5

    with expect_eperror():
        (a * b) << 5


@TestInstance
def test_function_lvalue():
    with expect_eperror():
        a = f_dwread_epd(0)
        a << 5


@TestInstance
def test_rvalue():
    from eudplib.core.variable.evcommon import _addor

    v1 = EUDVariable(0)

    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    v2 = v1 + 1 + EUDVariable(2) + 3 + EUDVariable(4) + 5
    ep_assert(trg_count + 5 == GetTriggerCounter(), "Failed to optimize rvalue")
    test_equality(
        "rvalue reuse test: self, __add__",
        [v2, f_dwread(trg + 344)],
        [15, EPD(v2.getValueAddr())],
    )

    trg = NextTrigger()
    v3 = v2 + EUDVariable(6)
    test_equality(
        "rvalue reuse test: other, __add__",
        [v3, f_dwread(trg + 4), f_dwread(trg + 344), f_dwread(trg + 348)],
        [21, v2.GetVTable(), EPD(v2.getDestAddr()), EPD(v3.getValueAddr())],
    )

    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    v4 = EUDVariable(20) - v2
    ep_assert(
        trg_count + 1 == GetTriggerCounter(),
        f"{trg_count} + 1 != {GetTriggerCounter()}",
    )
    nptr = f_dwread(v2.GetVTable() + 4)
    test_equality(
        "rvalue reuse test: self, __sub__",
        [v4, nptr, f_dwread(trg + 344), f_dwread(trg + 348), f_dwread(trg + 4)],
        [
            5,
            _addor.GetVTable(),
            EPD(v4.getValueAddr()),
            1,
            v2.GetVTable(),
        ],
    )

    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    v5 = v3 - EUDVariable(9)
    ep_assert(
        trg_count + 1 == GetTriggerCounter(),
        f"{trg_count} + 1 != {GetTriggerCounter()}",
    )
    test_equality(
        "rvalue reuse test: other, __sub__",
        [
            v5,
            f_dwread(trg + 4),
            f_dwread(trg + 328),
            f_dwread(trg + 344),
            f_dwread(trg + 348),
        ],
        [12, v3.GetVTable(), 0x55555555, EPD(v5.getValueAddr()), 0xFFFFFFFF],
    )

    with expect_eperror():
        SetVariables(f_dwread_epd(0), 0)
