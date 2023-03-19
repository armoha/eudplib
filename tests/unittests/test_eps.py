from collections import deque

from helper import *

from .test_eps_array import (
    DequeCases,
    DequeTest,
    f_test_compare,
    f_test_deque,
    f_test_queue,
    f_test_queue_wraparound,
    f_test_write,
)

# from .test_eps_bag import f_test_bag
from .test_eps_compat import f_test_compatibility, stat
from .test_eps_cunit import f_test_cunit
from .test_eps_epsfile import f_constv_thing, f_square, f_switch_test, f_test_array
from .test_eps_object import f_test_nested_object, f_test_object, f_test_selftype_member


@TestInstance
def test_epscript():
    test_equality("epScript compile 1", f_square(4), 16)
    test_equality("epScript compile 2", f_constv_thing(), 55)
    a = f_switch_test()
    test_equality(
        "epScript switch",
        [a[0], a[1], a[2], a[3], a[4], a[5]],
        [1239, 1243, 1246, 1256, 1258, 1260],
    )
    test_equality("epScript array", f_test_array(), 23)
    v = f_test_write()
    test_equality(
        "epScript array write",
        v[1:],
        [v[0]] * (len(v) - 1),
    )
    c = f_test_compare()
    test_equality(
        "epScript array compare",
        c[1:],
        [c[0]] * (len(c) - 1),
    )
    test_equality("epScript EUDQueue", f_test_queue(), 31)
    test_equality("epScript queue wraparound", f_test_queue_wraparound(), [0, 3, 9, 12, 9, 18, 13])
    dq = deque(maxlen=7)
    cases = []
    pushes = 1
    for method in DequeCases:
        if method in ("append", "appendleft"):
            f = getattr(dq, method)
            f(pushes)
            pushes += 1
        elif dq:
            f = getattr(dq, method)
            cases.append(f())
        else:
            cases.append(0)
    cases.append(len(dq) + sum(dq))
    testname = DequeTest + "".join(chr(14 + i % 4) + str(x) for i, x in enumerate(cases))
    test_equality("epScript EUDDeque %s" % testname, f_test_deque(), cases)

    test_equality("epScript object", f_test_object(), 511)
    test_equality("epScript nested object", f_test_nested_object(), 127)
    test_equality("epScript all object array", f_test_selftype_member(), 5)
    test_equality("epScript EPDCUnitMap", f_test_cunit(), 255)
    test_equality("epScript compatibility", f_test_compatibility(), 32)
    test_equality(
        "epScript stat_txt.tbl", stat.f_test_stattext(), [ord(c) for c in stat.expected_result]
    )
    # test_equality("epScript EUDBag", f_test_bag(), 555515)
