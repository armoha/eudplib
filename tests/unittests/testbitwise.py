from helper import *


@TestInstance
def test_bitwise():
    b1100 = EUDVariable(0b1100)
    b1010 = EUDVariable(0b1010)
    test_equality("f_bitand", f_bitand(b1100, b1010), 0b1100 & 0b1010)
    test_equality("f_bitor", f_bitor(b1100, b1010), 0b1100 | 0b1010)
    test_equality("f_bitxor", f_bitxor(b1100, b1010), 0b1100 ^ 0b1010)
    test_equality(
        "f_bitnand", f_bitnand(b1100, b1010), ~(0b1100 & 0b1010) & 0xFFFFFFFF
    )
    test_equality(
        "f_bitnor", f_bitnor(b1100, b1010), ~(0b1100 | 0b1010) & 0xFFFFFFFF
    )
    test_equality(
        "f_bitnxor", f_bitnxor(b1100, b1010), ~(0b1100 ^ 0b1010) & 0xFFFFFFFF
    )
    test_equality("f_bitnot", f_bitnot(b1100), ~0b1100 & 0xFFFFFFFF)
