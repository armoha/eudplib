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

from eudplib import utils as ut

from .. import core as c
from .tpatcher import PatchCondition


def _EUDBranchSub(conditions, ontrue, onfalse, *, _actions=None):
    """
    Reduced version of EUDBranch with following restructions.
    - All fields of conditions/actions should be constant.
    - type(conditions) is list
    - len(conditions) <= 16
    """
    assert len(conditions) <= 16

    brtrg = c.Forward()
    tjtrg = c.Forward()
    brtrg << c.RawTrigger(
        nextptr=onfalse, conditions=conditions, actions=c.SetNextPtr(brtrg, tjtrg)
    )
    if _actions is None:
        _actions = []
    _actions.append(c.SetNextPtr(brtrg, onfalse))
    tjtrg << c.RawTrigger(nextptr=ontrue, actions=_actions)


def EUDBranch(conditions, ontrue, onfalse, *, _actions=None):
    """Branch by whether conditions is satisfied or not.

    :param conditions: Nested list of conditions.
    :param ontrue: When all conditions are true, this branch is taken.
    :param onfalse: When any of the conditions are false, this branch is taken.
    """
    conditions = ut.FlattenList(conditions)
    conditions = list(map(PatchCondition, conditions))

    if len(conditions) == 0:
        c.RawTrigger(nextptr=ontrue)  # Just jump
        return

    # Check all conditions
    for i in range(0, len(conditions), 16):
        subontrue = c.Forward()
        subonfalse = onfalse

        if i + 16 < len(conditions):
            _EUDBranchSub(conditions[i : i + 16], subontrue, subonfalse)
            subontrue << c.NextTrigger()
            continue
        _EUDBranchSub(conditions[i:], subontrue, subonfalse, _actions=_actions)
        subontrue << ontrue
