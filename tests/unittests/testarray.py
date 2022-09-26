from helper import *


@TestInstance
def test_array():
    k = EUDArray(10)
    n = EUDVariable(k)
    b = EUDVariable()
    b << n
    a = EUDArray.cast(b)
    for i in range(10):
        a.set(i, 2**i)

    test_assert("Basic array test", [a[i] == 2**i for i in range(10)])
