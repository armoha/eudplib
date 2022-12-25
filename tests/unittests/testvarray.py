from helper import *

a_initials = ExprProxy([5] * 10)


@TestInstance
def test_varray():
    a = EUDVArray(len(a_initials))(a_initials)
    for i in range(8):
        a[i] = 2**i

    test_equality(
        "VArray test1",
        [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9]],
        [1, 2, 4, 8, 16, 32, 64, 128, 5, 5],
    )

    for i in EUDLoopRange(3, 6):
        a[i] = i * i * i

    test_equality(
        "VArray test2",
        [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9]],
        [1, 2, 4, 27, 64, 125, 64, 128, 5, 5],
    )

    b = EUDVariable(a)
    c = EUDVArray(8).cast(b)

    test_equality(
        "VArray test3",
        [c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]],
        [1, 2, 4, 27, 64, 125, 64, 128],
    )

    v_sum1 = EUDVariable()
    v_sum1 << 0
    for i in EUDLoopRange(0, 8):
        v_sum1 += c[i]

    test_equality("VArray test4", [v_sum1], [415])

    v_sum2 = EUDVariable()
    v_sum2 << 0
    for i in EUDLoopRange(0, 8):
        v_sum2 += c[i] * i

    test_equality("VArray test5", [v_sum2, a[9]], [2252, 5])
