#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
import functools

_signflag = c.EUDLightVariable()


def f_div_towards_zero(a, b, **kwargs) -> tuple[c.EUDVariable, c.EUDVariable] | tuple[int, int]:
    """Calculates the quotient and remainder of (a ÷ b), rounding the quotient towards zero.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    Consistent with C-like languages including JavaScript.
    """
    if c.IsEUDVariable(b):
        if not hasattr(f_div_towards_zero, "_eudf"):

            @c.EUDFunc
            def div_towards_zero_eud(a, b):
                return _div_towards_zero(a, b)

            setattr(f_div_towards_zero, "_eudf", div_towards_zero_eud)

        return getattr(f_div_towards_zero, "_eudf")(a, b, **kwargs)

    elif c.IsEUDVariable(a):
        return _div_towards_zero_const(b)(a, **kwargs)

    return int(a / b), a - int(a / b) * b


@functools.cache
def _div_towards_zero_const(b: int):
    @c.EUDFunc
    def f(a):
        return _div_towards_zero(a, b)

    return f


def _div_towards_zero(a, b):
    global _signflag
    _signflag << (0 if c.IsEUDVariable(b) else 2 * bool(b < 0))

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    if c.IsEUDVariable(b):
        c.RawTrigger(  # b is negative
            conditions=b >= 1 << 31,
            actions=(
                _signflag.AddNumber(2),
                b.ineg(action=True),
            ),
        )
    else:
        b = abs(b)

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


def f_div_floor(a, b, **kwargs) -> tuple[c.EUDVariable, c.EUDVariable] | tuple[int, int]:
    """Calculates the quotient and remainder of (a ÷ b), rounding the quotient towards negative infinity.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    Consistent with mathematical modulo.
    """
    if c.IsEUDVariable(b):
        if not hasattr(f_div_floor, "_eudf"):

            @c.EUDFunc
            def div_floor_eud(a, b):
                return _div_floor(a, b)

            setattr(f_div_floor, "_eudf", div_floor_eud)

        return getattr(f_div_floor, "_eudf")(a, b, **kwargs)

    elif c.IsEUDVariable(a):
        return _div_floor_const(b)(a, **kwargs)

    return divmod(a, b)


@functools.cache
def _div_floor_const(b: int):
    @c.EUDFunc
    def f(a):
        return _div_floor(a, b)

    return f


def _div_floor(a, b):
    global _signflag
    _signflag << (0 if c.IsEUDVariable(b) else 2 * bool(b < 0))

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    if c.IsEUDVariable(b):
        c.RawTrigger(  # b is negative
            conditions=b >= 1 << 31,
            actions=(
                _signflag.AddNumber(2),
                b.ineg(action=True),
            ),
        )
    else:
        b = abs(b)

    quotient, modulo = c.f_div(a, b)

    check, ontrue, onfalse = [c.Forward() for _ in range(3)]
    if c.IsEUDVariable(b):
        check << c.RawTrigger(  # modulo << -modulo + b
            nextptr=onfalse,
            conditions=(1 <= _signflag, _signflag <= 2, modulo >= 1),
            actions=[
                c.SetNextPtr(check, b.GetVTable()),
                c.SetNextPtr(b.GetVTable(), ontrue),
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                b.QueueAddTo(modulo),
            ],
        )
    else:
        check << c.RawTrigger(  # modulo << -modulo + b
            nextptr=onfalse,
            conditions=(1 <= _signflag, _signflag <= 2, modulo >= 1),
            actions=[
                c.SetNextPtr(check, ontrue),
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                modulo.AddNumber(b),
            ],
        )

    ontrue << c.RawTrigger(actions=c.SetNextPtr(check, onfalse))
    # when only one of divider or dividend is negative, quotient is negative
    onfalse << c.RawTrigger(
        conditions=(1 <= _signflag, _signflag <= 2),
        actions=quotient.ineg(action=True),
    )
    # when divider is negative, remainder is negative
    c.RawTrigger(
        conditions=_signflag.ExactlyX(2, 2),
        actions=modulo.ineg(action=True),
    )

    return quotient, modulo


def f_div_euclid(a, b, **kwargs) -> tuple[c.EUDVariable, c.EUDVariable] | tuple[int, int]:
    """Calculates the quotient and remainder of Euclidean division of a by b.

    Calculate signed division, unlike unsigned division `f_div(a, b)`.
    This computes the quotient such that `a = quotient * b + remainder`, and `0 <= r < abs(b)`.

    In other words, the result is a ÷ b rounded to the quotient such that `a >= quotient * b`.
    If `a > 0`, this is equal to round towards zero; if `a < 0`, this is equal to round towards +/- infinity (away from zero).
    """
    if c.IsEUDVariable(b):
        if not hasattr(f_div_euclid, "_eudf"):

            @c.EUDFunc
            def div_euclid_eud(a, b):
                return _div_euclid(a, b)

            setattr(f_div_euclid, "_eudf", div_euclid_eud)

        return getattr(f_div_euclid, "_eudf")(a, b, **kwargs)

    elif c.IsEUDVariable(a):
        return _div_euclid_const(b)(a, **kwargs)

    r = a - int(a / b) * b
    r = r + abs(b) if r < 0 else r
    return (a - r) // b, r


@functools.cache
def _div_euclid_const(b: int):
    @c.EUDFunc
    def f(a):
        return _div_euclid(a, b)

    return f


def _div_euclid(a, b):
    global _signflag
    _signflag << (0 if c.IsEUDVariable(b) else 2 * bool(b < 0))

    c.RawTrigger(  # a is negative
        conditions=a >= 1 << 31,
        actions=(
            _signflag.AddNumber(1),
            a.ineg(action=True),
        ),
    )
    if c.IsEUDVariable(b):
        c.RawTrigger(  # b is negative
            conditions=b >= 1 << 31,
            actions=(
                _signflag.AddNumber(2),
                b.ineg(action=True),
            ),
        )
    else:
        b = abs(b)

    quotient, modulo = c.f_div(a, b)

    check, ontrue, onfalse = [c.Forward() for _ in range(3)]
    if c.IsEUDVariable(b):
        check << c.RawTrigger(  # modulo << -modulo + b
            nextptr=onfalse,
            conditions=(_signflag.ExactlyX(1, 1), modulo >= 1),
            actions=[
                c.SetNextPtr(check, b.GetVTable()),
                c.SetNextPtr(b.GetVTable(), ontrue),
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                b.QueueAddTo(modulo),
            ],
        )
    else:
        check << c.RawTrigger(  # modulo << -modulo + b
            nextptr=onfalse,
            conditions=(_signflag.ExactlyX(1, 1), modulo >= 1),
            actions=[
                c.SetNextPtr(check, ontrue),
                quotient.AddNumber(1),
                modulo.ineg(action=True),
                modulo.AddNumber(b),
            ],
        )

    ontrue << c.RawTrigger(actions=c.SetNextPtr(check, onfalse))
    # when only one of divider or dividend is negative, quotient is negative
    onfalse << c.RawTrigger(
        conditions=(1 <= _signflag, _signflag <= 2),
        actions=quotient.ineg(action=True),
    )

    return quotient, modulo
