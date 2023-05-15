#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut
from eudplib.localize import _


def EUDBinaryMax(cond, minv=0, maxv=0xFFFFFFFF) -> c.EUDVariable:  # noqa: N802
    """Find maximum x satisfying cond(x) using binary search

    :param cond: Test condition
    :param minv: Minimum value in domain
    :param maxv: Maximum value in domain

    Cond should be binary classifier, meaning that for some N
        for all x > N, cond(x) is false.
        for all x <= N, cond(x) is true
    Then EUDBinaryMin will find such N.

    .. note:: If none of the value satisfies condition, then this
        function will return maxv.
    """
    if isinstance(minv, int) and isinstance(maxv, int):
        ut.ep_assert(minv <= maxv)
        r = maxv - minv
        if r <= 0:
            raise ut.EPError(_("maxv must be greater than minv"))
    else:
        r = None

    x = c.EUDVariable()
    nth = 0
    for i in range(31, -1, -1):
        if r and 2**i > r:
            continue

        if nth == 0:
            x << minv + 2**i
            if cs.EUDIfNot()(cond(x)):
                cs.DoActions(x.SubtractNumber(2**i))
            cs.EUDEndIf()
        else:
            x += 2**i
            if cs.EUDIfNot()([x <= maxv, cond(x)]):
                cs.DoActions(x.SubtractNumber(2**i))
            cs.EUDEndIf()
        nth += 1

    return x


def EUDBinaryMin(cond, minv=0, maxv=0xFFFFFFFF) -> c.EUDVariable:  # noqa: N802
    """Find minimum x satisfying cond(x) using binary search

    :param cond: Test condition
    :param minv: Minimum value in domain
    :param maxv: Maximum value in domain

    Cond should be binary classifier, meaning that for some N
        for all x < N, cond(x) is false.
        for all x >= N, cond(x) is true
    Then EUDBinaryMin will find such N

    .. note:: If none of the value satisfies condition, then this
        function will return maxv.
    """
    if isinstance(minv, int) and isinstance(maxv, int):
        ut.ep_assert(minv <= maxv)
        r = maxv - minv
        if r <= 0:
            raise ut.EPError(_("maxv must be greater than minv"))
    else:
        r = None

    x = c.EUDVariable()
    nth = 0
    for i in range(31, -1, -1):
        if r and 2**i > r:
            continue

        if nth == 0:
            x << maxv - 2**i
            if cs.EUDIfNot()(cond(x)):
                x += 2**i
            cs.EUDEndIf()
        else:
            if cs.EUDIf()(x >= 2**i):
                cs.DoActions(x.SubtractNumber(2**i))
                if cs.EUDIfNot()([x >= minv, cond(x)]):
                    x += 2**i
                cs.EUDEndIf()
            cs.EUDEndIf()
        nth += 1

    return x
