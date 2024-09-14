# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from ..trigger.tpatcher import negate_cond
from ..utils.eperror import EPError
from .simpleblock import EUDElse, EUDElseIf, EUDElseIfNot, EUDEndIf, EUDIf, EUDIfNot


def EUDOr(cond1, *conds) -> c.EUDLightBool:  # noqa: N802
    """cond1 || cond2 || ... || condn

    .. warning:: Short circuiting is not supported

    :param conds: List of conditions
    """

    v = c.EUDLightBool()
    if EUDIf()(cond1):
        c.RawTrigger(actions=v.Set())
    for cond in conds:
        if EUDElseIf()(cond):
            c.RawTrigger(actions=v.Set())
    if EUDElse()():
        c.RawTrigger(actions=v.Clear())
    EUDEndIf()
    return v


def EUDAnd(cond1, *conds) -> c.EUDLightBool:  # noqa: N802
    """cond1 && cond2 && ... && condn

    .. note::
        This function computes AND value of various conditions.
        If you don't want to do much computation, you should better use
        plain list instead of this function.

    .. warning:: Short circuiting is not supported.

    :param conds: List of conditions
    """

    v = c.EUDLightBool()
    if EUDIfNot()(cond1):
        c.RawTrigger(actions=v.Clear())
    for cond in conds:
        if EUDElseIfNot()(cond):
            c.RawTrigger(actions=v.Clear())
    if EUDElse()():
        c.RawTrigger(actions=v.Set())
    EUDEndIf()
    return v


def EUDNot(cond):  # noqa: N802
    """!cond

    :param conds: Condition to negate
    """

    if c.IsEUDVariable(cond):
        # TODO: better handle !v in conditional
        v = c.EUDVariable()
        v << 0
        c.RawTrigger(conditions=cond.Exactly(0), actions=v.SetNumber(1))
        return v

    if isinstance(cond, bool):
        if cond:
            return False
        return True
    try:
        return negate_cond(cond)
    except (AttributeError, EPError):
        pass
    v = c.EUDLightBool()
    c.RawTrigger(actions=v.Set())
    if EUDIf()(cond):
        c.RawTrigger(actions=v.Clear())
    EUDEndIf()
    return v
