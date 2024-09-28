# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TypeAlias

from .. import core as c
from .. import utils as ut
from ..core import ConstExpr, EUDVariable, RlocInt_C
from ..core.eudfunc.eudf import _EUDPredefineParam
from ..core.rawtrigger.constenc import SetTo, TrgModifier

_lowordfilter = c.EUDXVariable(0, SetTo, 0, 0xFFFF)
_lsbytefilter = c.EUDXVariable(0, SetTo, 0, 0xFF)
_lobytefilter = c.EUDXVariable(0, SetTo, 0, 0xFF00)
_hibytefilter = c.EUDXVariable(0, SetTo, 0, 0xFF0000)
_msbytefilter = c.EUDXVariable(0, SetTo, 0, 0xFF000000)

Constant: TypeAlias = ConstExpr | int | RlocInt_C
_fillers_use_seqcompute: list[
    tuple[
        Constant | EUDVariable,
        TrgModifier | None,
        Constant | EUDVariable,
    ]
] = []


def _flush_filler():
    global _fillers_use_seqcompute
    if _fillers_use_seqcompute:
        c.SeqCompute(_fillers_use_seqcompute)
        _fillers_use_seqcompute.clear()


def _filldw(dstepd: Constant | EUDVariable, v1: Constant | EUDVariable) -> None:
    _fillers_use_seqcompute.append((dstepd, c.SetTo, v1))


def _fillloword(dstepd: Constant, v1: EUDVariable) -> None:
    _fillers_use_seqcompute.extend(
        (
            (_lowordfilter, c.SetTo, v1),
            (dstepd, None, _lowordfilter),
        )
    )


def _filllsbyte(dstepd: Constant, v1: EUDVariable) -> None:
    _fillers_use_seqcompute.extend(
        (
            (_lsbytefilter, c.SetTo, v1),
            (dstepd, None, _lsbytefilter),
        )
    )


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill_b__(v1) -> None:
    _lobytefilter << 0
    for i in ut._rand_lst(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_lobytefilter.AddNumber(2 ** (i + 8)),
        )


def _filllobyte(dstepd: Constant, v1: Constant | EUDVariable) -> None:
    _flush_filler()
    _fill_b__(v1)
    _fillers_use_seqcompute.append((dstepd, None, _lobytefilter))


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill__b_(v1) -> None:
    _hibytefilter << 0
    for i in ut._rand_lst(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_hibytefilter.AddNumber(2 ** (i + 16)),
        )


def _fillhibyte(dstepd: Constant, v1: Constant | EUDVariable) -> None:
    _flush_filler()
    _fill__b_(v1)
    _fillers_use_seqcompute.append((dstepd, None, _hibytefilter))


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill___b(v1) -> None:
    _msbytefilter << 0
    for i in ut._rand_lst(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_msbytefilter.AddNumber(2 ** (i + 24)),
        )


def _fillmsbyte(dstepd: Constant, v1: Constant | EUDVariable) -> None:
    _flush_filler()
    _fill___b(v1)
    _fillers_use_seqcompute.append((dstepd, None, _msbytefilter))
