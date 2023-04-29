#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterable, Sequence

from eudplib import utils as ut

from .. import core as c
from ..core import Condition, Forward, RawTrigger
from ..core.rawtrigger.rawtriggerdef import _Action
from .tpatcher import PatchCondition, _Condition


def _EUDBranchSub(
    conditions: Sequence[Condition],
    ontrue: c.ConstExpr,
    onfalse: c.ConstExpr,
    *,
    _actions: _Action | None = None,
) -> None:
    """
    Reduced version of EUDBranch with following restructions.
    - All fields of conditions/actions should be constant.
    - type(conditions) is list
    - len(conditions) <= 16
    """
    ut.ep_assert(len(conditions) <= 16)

    brtrg = Forward()
    tjtrg = Forward()
    brtrg << RawTrigger(
        nextptr=onfalse, conditions=conditions, actions=c.SetNextPtr(brtrg, tjtrg)
    )
    if _actions:
        actions = ut.FlattenList(_actions)
    else:
        actions = []
    actions.append(c.SetNextPtr(brtrg, onfalse))
    tjtrg << RawTrigger(nextptr=ontrue, actions=actions)


def EUDBranch(
    conditions: _Condition | Iterable[_Condition | Iterable],
    ontrue: c.ConstExpr,
    onfalse: c.ConstExpr,
    *,
    _actions: _Action | None = None,
) -> None:
    """Branch by whether conditions is satisfied or not.

    :param conditions: Nested list of conditions.
    :param ontrue: When all conditions are true, this branch is taken.
    :param onfalse: When any of the conditions are false, this branch is taken.
    """
    conditions = ut.FlattenList(conditions)
    conds = list(map(PatchCondition, conditions))

    if len(conds) == 0:
        RawTrigger(nextptr=ontrue, actions=_actions)  # Just jump
        return

    # Check all conditions
    for i in range(0, len(conds), 16):
        subontrue = Forward()
        subonfalse = onfalse

        if i + 16 < len(conds):
            _EUDBranchSub(conds[i : i + 16], subontrue, subonfalse)
            subontrue << c.NextTrigger()
            continue
        _EUDBranchSub(conds[i:], subontrue, subonfalse, _actions=_actions)
        subontrue << ontrue
