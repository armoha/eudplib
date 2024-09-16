# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterable

from .. import core as c
from .. import utils as ut
from ..localize import _
from .tpatcher import patch_action, patch_condition

Conditions = (
    c.Condition | bool | Iterable[c.Condition | bool | Iterable | None] | None
)
Actions = c.Action | Iterable[c.Action | Iterable | None] | None


def Trigger(  # noqa: N802
    conditions: Conditions = None,
    actions: Actions = None,
    preserved: bool = True,
) -> tuple[c.Forward, c.RawTrigger]:
    """General easy-to-use trigger

    :param conditions: List of conditions. If there are none, trigger will
        always execute.
    :param actions: List of actions. If there are none, trigger will have no
        actions.
    :param preserved: Is trigger preserved? True by default.

    .. note::
        This is 'extended' trigger. All conditions and variables can contain
        `EUDVariable` object, and there may be more than 16 conditions and 64
        actions. Trigger internally uses `RawTrigger`.
    """

    ut.ep_assert(isinstance(preserved, bool), _("preserved should be bool"))

    if conditions is None:
        conditions = []
    if actions is None:
        actions = []

    conditions = ut.FlattenList(conditions)
    actions = ut.FlattenList(actions)
    tstart = c.NextTrigger()

    # Normal
    if len(conditions) <= 16 and len(actions) <= 64:
        patched_conds = []
        for cond in conditions:
            patched_conds.append(patch_condition(cond))

        patched_actions = []
        for act in actions:
            patched_actions.append(patch_action(act))

        tend = c.RawTrigger(
            conditions=patched_conds,
            actions=patched_actions,
            preserved=preserved,
        )

    else:
        # Extended trigger
        condts = []
        cend = c.Forward()

        # Check conditions
        for i in range(0, len(conditions), 16):
            conds = conditions[i : i + 16]
            cts = c.Forward()

            patched_conds = []
            for cond in conds:
                patched_conds.append(patch_condition(cond))

            nextcond = c.Forward()
            cts << c.RawTrigger(
                nextptr=cend,
                conditions=patched_conds,
                actions=c.SetNextPtr(cts, nextcond),
            )
            nextcond << c.NextTrigger()

            condts.append(cts)

        skipt = c.Forward()
        if not preserved:
            actions.append(c.SetNextPtr(tstart, skipt))

        # Execute actions
        for i in range(0, len(actions), 64):
            acts = actions[i : i + 64]
            patched_actions = []
            for act in acts:
                patched_actions.append(patch_action(act))

            tend = c.RawTrigger(actions=patched_actions)

        if not preserved:
            c.SetNextTrigger(skipt)

        # Revert conditions
        cend << c.NextTrigger()
        for i in range(0, len(condts), 64):
            tend = c.RawTrigger(
                actions=[c.SetNextPtr(cts, cend) for cts in condts[i : i + 64]]
            )

        if not preserved:
            skipt << c.NextTrigger()

    return tstart, tend
