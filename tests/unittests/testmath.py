import random
from helper import *


@TestInstance
def test_atan2():
    atanarray = EUDArray(360)
    for angle in EUDLoopRange(360):
        EP_SetRValueStrictMode(False)
        x, y = f_lengthdir(1000, angle)
        EP_SetRValueStrictMode(True)
        atanarray[angle] = f_atan2(y, x)

    # Value of atan2 may vary by 1 due to rounding error.
    # Here we check similarity.
    test_assert("atan2 test", [atanarray[angle] - angle + 1 <= 2 for angle in range(360)])

    atan256array = EUDArray(256)
    for angle in EUDLoopRange(256):
        EP_SetRValueStrictMode(False)
        x, y = f_lengthdir_256(1000, angle)
        EP_SetRValueStrictMode(True)
        atan256array[angle] = f_atan2_256(y, x)

    # Value of atan2 may vary by 1 due to rounding error.
    # Here we check similarity.
    test_assert("atan2_256 test", [atan256array[angle] - angle + 1 <= 2 for angle in range(256)])


@TestInstance
def test_specialized_div():
    x = EUDVariable()
    for i in range(0, 32):
        a = random.randint(1, 0xFFFFFFFF)
        b = 2 << i
        q, r = int(a / b), a - int(a / b) * b
        x << a
        test_equality(
            f"div_by_pow_of_2({a}, {b}) = {(q, r)}",
            f_div(x, b),
            [q, r],
        )


@TestInstance
def test_signed_div():
    for nth in range(4):
        for _ in range(4):
            a = random.randint(1, 0x7FFFFFFF)
            b = random.randint(1, a)
            if nth >= 2:
                a = -a
            if nth % 2 == 1:
                b = -b
            q, r = int(a / b), a - int(a / b) * b

            x = a if random.random() < 0.5 else EUDVariable(a)
            y = b if random.random() < 0.5 else EUDVariable(b)
            s = "EV{}".format(a) if IsEUDVariable(x) else str(a)
            t = "EV{}".format(b) if IsEUDVariable(y) else str(b)

            test_equality(
                f"div_towards_zero({s}, {t}) = {(q, r)}",
                f_div_towards_zero(x, y),
                [q, r],
            )

            EP_SetRValueStrictMode(False)
            test_equality(f"div_floor({s}, {t}) = {divmod(a, b)}", f_div_floor(x, y), divmod(a, b))

            # https://github.com/rust-lang/rust/blob/91eb6f9acfcfde6832d547959ad2d95b1ac0b5dc/library/core/src/num/int_macros.rs#L2115-L2130
            r = r + abs(b) if r < 0 else r
            q = (a - r) // b
            test_equality(f"div_euclid({s}, {t}) = {(q, r)})", f_div_euclid(x, y), [q, r])
            EP_SetRValueStrictMode(True)


test_operator("Square root", f_sqrt, lambda x: int(x**0.5))
