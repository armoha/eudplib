from helper import *


@TestInstance
def test_parse():
    a = Db(" \t\n-07285AC")
    EP_SetRValueStrictMode(False)
    number, digit = f_parse(a)
    test_equality("Decimal number", [number, digit], [-7285 & 0xFFFFFFFF, 4])
    number, digit = f_parse(a, 16)
    test_equality("Hexadecimal number", [number, digit], [-0x7285AC & 0xFFFFFFFF, 6])
    a = Db("\f -0B1101bftx")
    number, digit = f_parse(a, 0)
    test_equality("Binary number", [number, digit], [-0b1101 & 0xFFFFFFFF, 4])
    number, digit = f_parse(a, 16)
    test_equality("Hexadecimal number", [number, digit], [-0x1101BF & 0xFFFFFFFF, 6])
    a = Db("  \r +0o7426 -f")
    number, digit = f_parse(a, 0)
    EP_SetRValueStrictMode(True)
    test_equality("Octal number", [number, digit], [0o7426, 4])
