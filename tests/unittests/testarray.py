from helper import *
from random import randint


@TestInstance
def test_array():
    k = EUDArray(9)
    n = EUDVariable(k)
    b = EUDVariable()
    b << n
    a = EUDArray.cast(b)
    for i in range(9):
        a.set(i, 2**i)

    expect = [2**i for i in range(9)]
    test_equality("array ev.set(i, 2**i)", [a[i] for i in range(9)], expect)

    # constant array test
    EP_SetRValueStrictMode(False)

    for i in range(9):
        if i < 5:
            k[i] += 1 + i
        else:
            k[i] += EUDVariable(1 + i)
        expect[i] += 1 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array cn[i] += 1+i", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] -= 2 ** (10 - i)
        else:
            k[i] -= EUDVariable(2 ** (10 - i))
        expect[i] -= 2 ** (10 - i)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array cn[i] -= 2**(10-i)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] *= 3 * (i + 1)
        else:
            k[i] *= EUDVariable(3 * (i + 1))
        expect[i] *= 3 * (i + 1)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array cn[i] *= 3*(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] //= 7 * (i + 1)
        else:
            k[i] //= EUDVariable(7 * (i + 1))
        expect[i] //= 7 * (i + 1)
    test_equality("array cn[i] //= 7*(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] %= 9 ** (i + 1)
        else:
            k[i] %= EUDVariable(9 ** (i + 1))
        expect[i] %= 9 ** (i + 1)
    test_equality("array cn[i] %= 9**(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] <<= i + 1
        else:
            k[i] <<= EUDVariable(i + 1)
        expect[i] <<= i + 1
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array cn[i] <<= i+1", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            k[i] >>= 16 - i
        else:
            k[i] >>= EUDVariable(16 - i)
        expect[i] >>= 16 - i
    test_equality("array cn[i] >>= 16-i", [a[i] for i in range(9)], expect)

    """
    for i in range(9):
        if i < 5:
            k[i] **= 2 + i
        else:
            k[i] **= EUDVariable(2 + i)
        expect[i] **= 2 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array cn[i] **= 2+i", [a[i] for i in range(9)], expect)
    """

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            k[i] &= mask
        else:
            k[i] &= EUDVariable(mask)
        expect[i] &= mask
    test_equality(f"array cn[i] &= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            k[i] |= mask
        else:
            k[i] |= EUDVariable(mask)
        expect[i] |= mask
    test_equality(f"array cn[i] |= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            k[i] ^= mask
        else:
            k[i] ^= EUDVariable(mask)
        expect[i] ^= mask
    test_equality(f"array cn[i] ^= 0x{mask:X}", [a[i] for i in range(9)], expect)

    # casted array test

    for i in range(9):
        if i < 5:
            a[i] += 1 + i
        else:
            a[i] += EUDVariable(1 + i)
        expect[i] += 1 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[i] += 1+i", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] -= 2 ** (10 - i)
        else:
            a[i] -= EUDVariable(2 ** (10 - i))
        expect[i] -= 2 ** (10 - i)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[i] -= 2**(10-i)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] *= 3 * (i + 1)
        else:
            a[i] *= EUDVariable(3 * (i + 1))
        expect[i] *= 3 * (i + 1)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[i] *= 3*(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] //= 7 * (i + 1)
        else:
            a[i] //= EUDVariable(7 * (i + 1))
        expect[i] //= 7 * (i + 1)
    test_equality("array ev[i] //= 7*(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] %= 9 ** (i + 1)
        else:
            a[i] %= EUDVariable(9 ** (i + 1))
        expect[i] %= 9 ** (i + 1)
    test_equality("array ev[i] %= 9**(i+1)", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] <<= i + 1
        else:
            a[i] <<= EUDVariable(i + 1)
        expect[i] <<= i + 1
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[i] <<= i+1", [a[i] for i in range(9)], expect)

    for i in range(9):
        if i < 5:
            a[i] >>= 16 - i
        else:
            a[i] >>= EUDVariable(16 - i)
        expect[i] >>= 16 - i
    test_equality("array ev[i] >>= 16-i", [a[i] for i in range(9)], expect)

    """
    for i in range(9):
        if i < 5:
            a[i] **= 2 + i
        else:
            a[i] **= EUDVariable(2 + i)
        expect[i] **= 2 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[i] **= 2+i", [a[i] for i in range(9)], expect)
    """

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            a[i] &= mask
        else:
            a[i] &= EUDVariable(mask)
        expect[i] &= mask
    test_equality(f"array ev[i] &= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            a[i] |= mask
        else:
            a[i] |= EUDVariable(mask)
        expect[i] |= mask
    test_equality(f"array ev[i] |= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in range(9):
        if i < 5:
            a[i] ^= mask
        else:
            a[i] ^= EUDVariable(mask)
        expect[i] ^= mask
    test_equality(f"array ev[i] ^= 0x{mask:X}", [a[i] for i in range(9)], expect)

    # casted array with variable index test

    for i in EUDLoopRange(9):
        a[i] += 1 + i
    for i in range(9):
        expect[i] += 1 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[ev] += 1+i", [a[i] for i in range(9)], expect)

    x = EUDVariable(2**2)
    index = EUDVariable(9)
    if EUDWhile()(index >= 1):
        index -= 1
        a[index] -= x
        x += x
    EUDEndWhile()
    for i in range(9):
        expect[i] -= 2 ** (10 - i)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[ev] -= 2**(10-i)", [a[i] for i in range(9)], expect)

    for i in EUDLoopRange(9):
        a[i] *= 3 * (i + 1)
    for i in range(9):
        expect[i] *= 3 * (i + 1)
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[ev] *= 3*(i+1)", [a[i] for i in range(9)], expect)

    for i in EUDLoopRange(9):
        a[i] //= 7 * (i + 1)
    for i in range(9):
        expect[i] //= 7 * (i + 1)
    test_equality("array ev[ev] //= 7*(i+1)", [a[i] for i in range(9)], expect)

    x << 9**1
    for i in EUDLoopRange(9):
        a[i] %= x
        x *= 9
    for i in range(9):
        expect[i] %= 9 ** (i + 1)
    test_equality("array ev[ev] %= 9**(i+1)", [a[i] for i in range(9)], expect)

    for i in EUDLoopRange(9):
        a[i] <<= i + 1
    for i in range(9):
        expect[i] <<= i + 1
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[ev] <<= i+1", [a[i] for i in range(9)], expect)

    for i in EUDLoopRange(9):
        a[i] >>= 16 - i
    for i in range(9):
        expect[i] >>= 16 - i
    test_equality("array ev[ev] >>= 16-i", [a[i] for i in range(9)], expect)

    """
    for i in EUDLoopRange(9):
        a[i] **= 2 + i
    for i in range(9):
        expect[i] **= 2 + i
        expect[i] = expect[i] & 0xFFFFFFFF
    test_equality("array ev[ev] **= 2+i", [a[i] for i in range(9)], expect)
    """

    mask = randint(0, 0xFFFFFFFF)
    for i in EUDLoopRange(9):
        a[i] &= mask
    for i in range(9):
        expect[i] &= mask
    test_equality(f"array ev[ev] &= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in EUDLoopRange(9):
        a[i] |= mask
    for i in range(9):
        expect[i] |= mask
    test_equality(f"array ev[ev] |= 0x{mask:X}", [a[i] for i in range(9)], expect)

    mask = randint(0, 0xFFFFFFFF)
    for i in EUDLoopRange(9):
        a[i] ^= mask
    for i in range(9):
        expect[i] ^= mask
    test_equality(f"array ev[ev] ^= 0x{mask:X}", [a[i] for i in range(9)], expect)

    EP_SetRValueStrictMode(True)
