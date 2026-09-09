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

    # No rvalue (refcount-based) optimization: _is_rvalue() always returns
    # False, so __add__/__sub__ always allocate a fresh temporary via
    # SeqCompute([(t, SetTo, ...), (t, Add/Sub, ...)]). Name the operands
    # so the trigger-layout expectations can reference the actual
    # temporaries instead of assuming reuse (v2/v3/v4 reusing the operand).
    v1 = EUDVariable(0)
    c2 = EUDVariable(2)
    c4 = EUDVariable(4)
    c6 = EUDVariable(6)
    c9 = EUDVariable(9)
    c20 = EUDVariable(20)

    # self.__add__: v1 + 1 is evaluated first, so the first trigger's
    # first action epd slot holds EPD(t1), not EPD(v2).
    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    t1 = v1 + 1
    v2 = t1 + c2 + 3 + c4 + 5
    ep_assert(trg_count + 5 == GetTriggerCounter(), "No copy elision, TODO")
    test_equality(
        "rvalue reuse test: self, __add__",
        [v2, f_dwread(trg + 344)],
        [15, EPD(t1.getValueAddr())],
    )

    # other.__add__: v2 + c6 allocates fresh v3; first trigger chains
    # through c6, not v2.
    trg = NextTrigger()
    v3 = v2 + c6
    test_equality(
        "rvalue reuse test: other, __add__",
        [v3, f_dwread(trg + 4), f_dwread(trg + 344), f_dwread(trg + 348)],
        [21, c6.GetVTable(), EPD(c6.getDestAddr()), EPD(v3.getValueAddr())],
    )

    # self.__sub__ (c20 - v2): fresh v4 needs 2 triggers. First trigger
    # holds 0xFFFFFFFF (not 1), and v2's nextptr no longer points to
    # _addor (no reuse of self/other via VProc/__isub__).
    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    v4 = c20 - v2
    ep_assert(
        trg_count + 2 == GetTriggerCounter(),
        f"{trg_count} + 2 != {GetTriggerCounter()}",
    )
    nptr = f_dwread(v2.GetVTable() + 4)
    test_equality(
        "rvalue reuse test: self, __sub__",
        [v4, f_dwread(trg + 344), f_dwread(trg + 348), f_dwread(trg + 4)],
        [5, EPD(v4.getValueAddr()), 0xFFFFFFFF, v2.GetVTable()],
    )
    test_assert(
        "rvalue no-reuse test: self, __sub__ nextptr",
        nptr != _addor.GetVTable(),
    )

    # other.__sub__ (v3 - c9): fresh v5 needs 2 triggers. First trigger
    # chains through c9 with a plain SetDeaths (mask 0), not SetDeathsX
    # with 0x55555555.
    trg = NextTrigger()
    trg_count = GetTriggerCounter()
    v5 = v3 - c9
    ep_assert(
        trg_count + 2 == GetTriggerCounter(),
        f"{trg_count} + 2 != {GetTriggerCounter()}",
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
        [12, c9.GetVTable(), 0, EPD(v5.getValueAddr()), 0xFFFFFFFF],
    )
