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


test_operator("Square root", f_sqrt, lambda x: int(x**0.5))
