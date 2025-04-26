# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# This code uses simple LCG algorithm.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...core.eudfunc.eudf import _EUDPredefineReturn
from ...core.variable.vbase import VariableBase
from ...memio.rwcommon import lv

_seed = c.EUDVariable()


def f_getseed() -> c.EUDVariable:
    t = c.EUDVariable()
    t << _seed
    return t


def f_srand(seed) -> None:
    _seed << seed


@c.EUDFunc
def f_randomize():
    global _seed

    # Store switch 1
    end = c.Forward()
    n = lv
    c.RawTrigger(
        actions=[
            _seed.SetNumber(0),
            _seed.QueueAddTo(_seed),
            c.SetMemoryX(end + 328 + 24, c.SetTo, 5 << 24, 0xFF << 24),
            n.SetNumber(32),
        ]
    )
    c.RawTrigger(
        conditions=c.Switch("Switch 1", c.Set),
        actions=c.SetMemoryX(end + 328 + 24, c.SetTo, 4 << 24, 0xFF << 24),
    )

    if cs.EUDWhile()(n >= 1):
        # _seed += _seed
        c.VProc(
            _seed,
            [
                c.SetSwitch("Switch 1", c.Random),
                n.SubtractNumber(1),
            ],
        )
        c.RawTrigger(
            conditions=c.Switch("Switch 1", c.Set), actions=_seed.AddNumber(1)
        )
    cs.EUDEndWhile()

    end << c.RawTrigger(actions=c.SetSwitch("Switch 1", c.Set))


@_EUDPredefineReturn(2, 3)
@c.EUDFunc
def f_rand():
    ret = f_rand._frets[0]
    c.f_mul(_seed, 1103515245, ret=[_seed])
    c.VProc(_seed, [_seed.AddNumber(12345), _seed.QueueAssignTo(ret)])
    ret >>= 16
    # Only HIWORD is returned
    # return ret


@c.EUDFunc
def f_dwrand():
    dseed = c.f_mul(_seed, 1103515245)
    dseed += 12345
    c.f_mul(dseed, 1103515245, ret=[_seed])
    c.RawTrigger(
        actions=[
            _seed.AddNumber(12345),
            # HIWORD
            dseed.SetNumberX(0, 0xFFFF),
        ],
    )

    # LOWORD
    for i in range(16, 32):
        c.RawTrigger(
            conditions=_seed.AtLeastX(1, 2**i),
            actions=dseed.AddNumber(2 ** (i - 16)),
        )

    return dseed
