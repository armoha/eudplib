# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs


@c.EUDFunc
def _pow(a, b):
    ret, _2n = c.EUDCreateVariables(2)
    c.SetVariables([ret, _2n], [1, 1])
    # 2^n < b 인 모든 a^(2^n) 구하기
    if cs.EUDWhile()(_2n <= b):
        # b에 (2^n)이 있으면 답에 a^(2^n)을 곱한다
        if cs.EUDIf()(b.AtLeastX(1, _2n)):
            ret *= a
        cs.EUDEndIf()
        _2n += _2n
        a *= a
    cs.EUDEndWhile()
    return ret


def f_pow(a, b):
    """
    f_pow(a, b) calculates a ** b
    """
    if isinstance(a, int):
        # Constant base and exponent
        if isinstance(b, int):
            return a**b

        # Constant base and variable exponent
        if a == 0:
            ret = c.EUDVariable()
            ret << 0
            # 0**0 = 1
            c.RawTrigger(
                conditions=b.Exactly(0),
                actions=ret.SetNumber(1),
            )
            return ret
        if a == 1:
            return 1

        trailing_zeros = (a & -a).bit_length() - 1
        if trailing_zeros == 0:
            return _pow(a, b)

        odd_part = a >> trailing_zeros
        powered = 1 if odd_part == 1 else _pow(odd_part, b)
        shift = c.f_mul(b, trailing_zeros)
        return c.f_bitlshift(powered, shift)

    # Variable base
    return _pow(a, b)
