import random

from helper import *


@TestInstance
def test_parse():
    EP_SetRValueStrictMode(False)

    a = Db("dpdkfah")
    number, digit = f_parse(a)
    test_equality(
        "#0. Error handling: Not a number - return (0, 0)", [number, digit], [0, 0]
    )

    a = Db(" \t\n07285AC")
    number, digit = f_parse(a, 7)
    test_equality("#1. Parse 0 - return (0, 1)", [number, digit], [0, 1])
    number, digit = f_parse(a)
    test_equality("#2. Decimal number", [number, digit], [7285, 4])
    number, digit = f_parse(a, 16)
    test_equality("#3. Hexadecimal number", [number, digit], [0x7285AC, 6])

    a = Db("\f -0B1101bftx")
    number, digit = f_parse(a, 0)
    test_equality(
        "#4. radix=0: autodetect -Binary number",
        [number, digit],
        [-0b1101 & 0xFFFFFFFF, 4],
    )
    number, digit = f_parse(a, 16)
    test_equality(
        "#5. -Hexadecimal number", [number, digit], [-0xB1101BF & 0xFFFFFFFF, 7]
    )

    a = Db("  \r +0o7426 -f")
    number, digit = f_parse(a, 0)
    test_equality(
        "#6. radix=0: autodetect +Octal number", [number, digit], [0o7426, 4]
    )

    for n in range(7, 10):
        r = random.randint(0, 0x7FFFFFFF)
        a = Db(str(r))
        number, digit = f_parse(a)
        test_equality("#%u. Parse %u" % (n, r), [number, digit], [r, len(str(r))])

    a = Db("1" * 32)
    number, digit = f_parse(a)
    test_equality("Overflow: base 10", [number, digit], [0x7FFFFFFF, 10])
    for n in range(2, 37):
        # For overflow input, incorrect digits in base other than 10.
        number = f_parse(a, n)[0]
        test_equality("Overflow: base %u" % n, [number], [0x7FFFFFFF])

    EP_SetRValueStrictMode(True)
