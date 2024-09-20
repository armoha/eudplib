# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterable, Sequence

from .. import core as c
from .. import utils as ut
from ..core import Condition, ConstExpr
from ..core.rawtrigger.rawtriggerdef import _Action
from .tpatcher import _Condition, patch_condition


def _branch_sub(
    conditions: Sequence[Condition],
    ontrue: ConstExpr,
    onfalse: ConstExpr,
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

    brtrg = c.Forward()
    tjtrg = c.Forward()
    brtrg << c.RawTrigger(
        nextptr=onfalse, conditions=conditions, actions=c.SetNextPtr(brtrg, tjtrg)
    )
    actions: _Action = c.SetNextPtr(brtrg, onfalse)
    if _actions:
        _actions = ut.FlattenList(_actions)
        _actions.append(actions)
        actions = _actions
    tjtrg << c.RawTrigger(nextptr=ontrue, actions=actions)


def EUDBranch(  # noqa: N802
    conditions: _Condition | Iterable[_Condition | Iterable],
    ontrue: ConstExpr,
    onfalse: ConstExpr,
    *,
    _actions: _Action | None = None,
) -> None:
    """Branch by whether conditions is satisfied or not.

    :param conditions: Nested list of conditions.
    :param ontrue: When all conditions are true, this branch is taken.
    :param onfalse: When any of the conditions are false, this branch is taken.
    :param _actions: When all conditions are true, those actions are executed.
    """
    conditions = ut.FlattenList(conditions)
    conds = list(map(patch_condition, conditions))

    if len(conds) == 0:  # Just jump
        if _actions:
            c.RawTrigger(nextptr=ontrue, actions=_actions)
        else:
            c.SetNextTrigger(ontrue)
        return

    # Check all conditions
    for i in range(0, len(conds), 16):
        subontrue = c.Forward()
        subonfalse = onfalse

        if i + 16 < len(conds):
            _branch_sub(conds[i : i + 16], subontrue, subonfalse)
            subontrue << c.NextTrigger()
        else:
            _branch_sub(conds[i:], subontrue, subonfalse, _actions=_actions)
            subontrue << ontrue
