import random

from helper import *


@TestInstance
def test_arithmetics():
    EP_SetRValueStrictMode(False)

    v = random.randint(1, 0xFFFF)
    ev = EUDVariable()
    # const muldiv special cases
    for case in (-1, 0):
        ev << v
        ev *= case
        test_equality(f"{v} *= {case}", ev, (v * case) & 0xFFFFFFFF)
    for power in range(1, 8):
        case = 2**power
        ev << v
        ev *= case
        test_equality(f"{v} *= {case}", ev, (v * case) & 0xFFFFFFFF)

    ev << v
    ev //= 0
    test_equality(f"{v} //= 0", ev, 0xFFFFFFFF)
    ev << v
    ev %= 0
    test_equality(f"{v} %= 0", ev, v)
    ev << v
    ev //= 1
    test_equality(f"{v} //= 1", ev, v)
    ev << v
    ev %= 1
    test_equality(f"{v} %= 1", ev, 0)

    for _ in range(5):
        r = random.randint(3, 0xFFFFFFFF)
        ev << v
        ev *= r
        test_equality(f"{v} *= {r}", ev, (v * r) & 0xFFFFFFFF)

    for _ in range(5):
        r = random.randint(2, 0xFFFF)
        ev << v
        ev << f_pow(ev, r)
        test_equality(f"{v} ** {r}", ev, (v**r) & 0xFFFFFFFF)

    EP_SetRValueStrictMode(True)
