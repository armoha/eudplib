#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

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

from .. import core as c
from .tpatcher import PatchCondition, PatchAction
from eudplib import utils as ut
from eudplib.localize import _


def Trigger(conditions=None, actions=None, preserved=True):
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
            patched_conds.append(PatchCondition(cond))

        patched_actions = []
        for act in actions:
            patched_actions.append(PatchAction(act))

        tend = c.RawTrigger(
            conditions=patched_conds, actions=patched_actions, preserved=preserved
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
                patched_conds.append(PatchCondition(cond))

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
            actions.append(c.SetNextPtr(start, skipt))

        # Execute actions
        for i in range(0, len(actions), 64):
            acts = actions[i : i + 64]
            patched_actions = []
            for act in acts:
                patched_actions.append(PatchAction(act))

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

    return (tstart, tend)
