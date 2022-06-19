from helper import *


@TestInstance
def test_pvariable():
    a = PVariable([5, 5, 5, 5, 5, 5, 5, 5])
    for i in range(7):
        a[i] = 2**i  # (1, 2, 4, 8, 16, 32, 64, 5)

    for i in EUDLoopRange(2, 5):
        a[i] = i * i * i  # (1, 2, 8, 27, 64, 32, 64, 5)

    b = EUDVariable(a)
    c = PVariable.cast(b)

    v_sum = EUDVariable()
    n = EUDVariable(1)
    for i in EUDLoopRange(0, 8):
        v_sum += a[i] * n
        n += 1

    test_equality("PVariable test", [v_sum, a[7]], [1137, 5])

    @EUDTypedFunc([PVariable])
    def sub1(v):
        for i in EUDLoopRange(8):
            v[i] -= 1

    @EUDTypedFunc([PVariable])
    def sub1i(v):
        for i in EUDLoopRange(8):
            v[i] -= 1 + i

    sub1(a)
    test_equality(
        "PVariable -= 1 test",
        [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]],
        [0, 1, 7, 26, 63, 31, 63, 4],
    )

    sub1i(a)
    test_equality(
        "PVariable -= var test",
        [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]],
        [0xFFFFFFFF, 0xFFFFFFFF, 4, 22, 58, 25, 56, 0xFFFFFFFC],
    )
