#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
from ... import core as c
from ... import ctrlstru as cs

_signflag = c.EUDLightVariable()


@c.EUDFunc
def f_div_towards_zero(a, b):
    """Calculates the quotient and remainder of (a ÷ b), rounding the quotient towards zero.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    Consistent with C-like languages including JavaScript.
    """
    global _signflag
    _signflag << 0

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    c.RawTrigger(  # b is negative
        conditions=b >= 1 << 31,
        actions=(
            _signflag.AddNumber(2),
            b.ineg(action=True),
        ),
    )

    quotient, modulo = c.f_div(a, b)

    # when only one of divider or dividend is negative, quotient is negative
    c.RawTrigger(
        conditions=(1 <= _signflag, _signflag <= 2),
        actions=quotient.ineg(action=True),
    )
    # when dividend is negative, modulo is negative
    c.RawTrigger(
        conditions=_signflag.ExactlyX(1, 1),
        actions=modulo.ineg(action=True),
    )

    return quotient, modulo


@c.EUDFunc
def f_div_floor(a, b):
    """Calculates the quotient and remainder of (a ÷ b), rounding the quotient towards negative infinity.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    Consistent with mathematical modulo.
    """
    global _signflag
    _signflag << 0

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    c.RawTrigger(  # b is negative
        conditions=b >= 1 << 31,
        actions=(
            _signflag.AddNumber(2),
            b.ineg(action=True),
        ),
    )

    quotient, modulo = c.f_div(a, b)

    if cs.EUDIf()((1 <= _signflag, _signflag <= 2, modulo >= 1)):
        # modulo << -modulo + b
        c.VProc(
            b,
            [
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                b.QueueAddTo(modulo),
            ],
        )
    cs.EUDEndIf()
    # when only one of divider or dividend is negative, quotient is negative
    c.RawTrigger(
        conditions=(1 <= _signflag, _signflag <= 2),
        actions=quotient.ineg(action=True),
    )
    # when divider is negative, remainder is negative
    c.RawTrigger(
        conditions=_signflag.ExactlyX(2, 2),
        actions=modulo.ineg(action=True),
    )

    return quotient, modulo


@c.EUDFunc
def f_div_euclid(a, b):
    """Calculates the quotient and remainder of Euclidean division of a by b.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    This computes the quotient such that `a = quotient * b + remainder`, and `0 <= r < abs(b)`.

    In other words, the result is a ÷ b rounded to the quotient such that `a >= quotient * b`.
    If `a > 0`, this is equal to round towards zero; if `a < 0`, this is equal to round towards +/- infinity (away from zero).
    """
    _signflag << 0

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    c.RawTrigger(  # b is negative
        conditions=b >= 1 << 31,
        actions=(
            _signflag.AddNumber(2),
            b.ineg(action=True),
        ),
    )

    quotient, modulo = c.f_div(a, b)

    if cs.EUDIf()((_signflag.ExactlyX(1, 1), modulo >= 1)):
        # modulo << -modulo + b
        c.VProc(
            b,
            [
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                b.QueueAddTo(modulo),
            ],
        )
    cs.EUDEndIf()
    # when only one of divider or dividend is negative, quotient is negative
    c.RawTrigger(
        conditions=(1 <= _signflag, _signflag <= 2),
        actions=quotient.ineg(action=True),
    )

    return quotient, modulo
