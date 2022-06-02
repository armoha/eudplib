#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Armoha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from eudplib import core as c, ctrlstru as cs, utils as ut


@c.EUDFunc
def _pow(a, b):
    ret, _2n = c.EUDCreateVariables(2)
    c.SetVariables([ret, _2n], [1, 1])
    # 2^n < b 인 모든 a^(2^n) 구하기
    if cs.EUDWhile()(_2n < b):
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
