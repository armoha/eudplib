#!/usr/bin/python
# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs


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
    if isinstance(a, int) and isinstance(b, int):
        return a**b
    return _pow(a, b)
