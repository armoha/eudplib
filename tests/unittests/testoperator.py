from helper import *


test_operator("Multiplication", lambda x, y: x * y)
test_operator("Division", lambda x, y: x // y)
test_operator("Remainder", lambda x, y: x % y)
test_operator("Bitwise and", lambda x, y: x & y)
test_operator("Bitwise or", lambda x, y: x | y)
test_operator("Bitwise xor", lambda x, y: x ^ y)
test_operator("lshift", lambda x, y: f_bitlshift(x, y % 32))
test_operator("rshift", lambda x, y: f_bitrshift(x, y % 32))


@TestInstance
def test_variable_inequal():
    a, b, c, d = EUDCreateVariables(4)
    a << 1
    b << 1
    c << 2
    d << 2

    test_assert("never", EUDNot([a != b]))
    test_assert("never2", EUDNot([(a - b).AtLeast(1)]))
    test_assert("never and never", EUDNot([a != b, c != d]))
    test_assert("never(c) and never(c)", EUDNot([Never(), Never()]))
    test_assert("never and never(c)", EUDNot([a != b, Never()]))
    test_assert("never(c) and never", EUDNot([Never(), c != d]))

    test_assert("__lt__", a < c)
    test_assert("__le__", a <= c)
    test_assert("__le__", a <= b)
    test_assert("__le__", EUDNot(c <= a))  # a < c
