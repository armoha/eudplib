from helper import *


a = EUDVariable(0)


@EUDFunc
def f_func_with_side_effect(b):
    global a
    a += 1
    return b


@TestInstance
def test_eudscand():
    test_assert("EUDSCAnd w. (true, true)", EUDSCAnd()(Always())(Always())())
    test_assert("EUDSCAnd w. (true, false)", EUDNot(EUDSCAnd()(Always())(Never())()))
    test_assert("EUDSCAnd w. (false, false)", EUDNot(EUDSCAnd()(Never())(Never())()))

    # Check short-circuiting. f_func_with_side_effect should not be executed
    a << 0
    cv = EUDSCAnd()(Never())(f_func_with_side_effect(1))()
    test_assert("EUDSCAnd w. (false, true (side_effect)", EUDNot(cv))
    test_equality("EUDSCAnd w. (false, true (side_effect)", a, 0)

    # Check short-circuiting 2. f_func_with_side_effect should not be executed
    a << 0
    cv = EUDSCAnd()(f_func_with_side_effect(1))(f_func_with_side_effect(1))(
        f_func_with_side_effect(0)
    )(f_func_with_side_effect(1))()
    test_assert("EUDSCAnd w. (t, t, f, t)", EUDNot(cv))
    test_equality("EUDSCAnd w. (t, t, f, t)", a, 3)


@TestInstance
def test_eudscor():
    test_assert("EUDSCOr w. (true, true)", EUDSCOr()(Always())(Always())())
    test_assert("EUDSCOr w. (true, false)", EUDSCOr()(Always())(Never())())
    test_assert("EUDSCOr w. (false, false)", EUDNot(EUDSCOr()(Never())(Never())()))

    # Check short-circuiting. f_func_with_side_effect should not be executed
    a << 0
    cv = EUDSCOr()(Always())(f_func_with_side_effect(1))()
    test_assert("EUDSCOr w. (true, true (side_effect)", cv)
    test_equality("EUDSCOr w. (true, true (side_effect)", a, 0)

    # Check short-circuiting 2. f_func_with_side_effect should not be executed
    a << 0
    cv = EUDSCOr()(f_func_with_side_effect(0))(f_func_with_side_effect(0))(
        f_func_with_side_effect(1)
    )(f_func_with_side_effect(1))()
    test_assert("EUDSCOr w. (f, f, t, t)", cv)
    test_equality("EUDSCOr w. (f, f, t, t)", a, 3)
