from helper import *

from .test_eps_array import f_test_compare, f_test_write
from .test_eps_epsfile import f_constv_thing, f_square, f_switch_test, f_test_array


@TestInstance
def test_epscript():
    test_equality("epScript compile test", f_square(4), 16)
    test_equality("epScript compile test", f_constv_thing(), 55)
    a = f_switch_test()
    test_equality(
        "epScript switch test",
        [a[0], a[1], a[2], a[3], a[4], a[5]],
        [1239, 1243, 1246, 1256, 1258, 1260],
    )
    test_equality(
        "epScript array test",
        f_test_array(),
        23,
    )
    v = f_test_write()
    test_equality(
        "epScript array write test",
        v[1:],
        [v[0]] * (len(v) - 1),
    )
    c = f_test_compare()
    test_equality(
        "epScript array compare test",
        c[1:],
        [c[0]] * (len(c) - 1),
    )
