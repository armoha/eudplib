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

from ..eudobj import EUDObject, Db
from .triggerscope import NextTrigger, _RegisterTrigger
from .condition import Condition
from eudplib import utils as ut


# Trigger counter thing

_trgCounter = 0


def GetTriggerCounter():
    return _trgCounter


# Aux


def _bool2Cond(x):
    if x is True:
        return Condition(0, 0, 0, 0, 0, 22, 0, 0)  # Always
    elif x is False:
        return Condition(0, 0, 0, 0, 0, 23, 0, 0)  # Never
    else:
        return x


def Disabled(arg):
    """Disable condition or action"""
    arg.Disabled()


# RawTrigger


class RawTrigger(EUDObject):
    def __init__(
        self,
        prevptr=None,
        nextptr=None,
        conditions=None,
        actions=None,
        *args,
        preserved=True,
        trigSection=None
    ):
        super().__init__()

        # Register trigger to global table
        global _trgCounter
        _trgCounter += 1
        _RegisterTrigger(self)  # This should be called before (1)

        # Set linked list pointers
        if prevptr is None:
            prevptr = 0
        if nextptr is None:
            nextptr = NextTrigger()  # (1)

        self._prevptr = prevptr
        self._nextptr = nextptr

        # Uses normal condition/action initialization
        if trigSection is None:
            # Normalize conditions/actions
            if conditions is None:
                conditions = []
            conditions = ut.FlattenList(conditions)
            conditions = list(map(_bool2Cond, conditions))

            if actions is None:
                actions = []
            actions = ut.FlattenList(actions)

            ut.ep_assert(len(conditions) <= 16, "Too many conditions")
            ut.ep_assert(len(actions) <= 64, "Too many actions")

            # Register condition/actions to trigger
            for i, cond in enumerate(conditions):
                cond.CheckArgs(i)
                cond.SetParentTrigger(self, i)

            for i, act in enumerate(actions):
                act.CheckArgs(i)
                act.SetParentTrigger(self, i)

            self._conditions = conditions
            self._actions = actions
            self.preserved = preserved

        # Uses trigger segment for initialization
        # NOTE : player information is lost inside eudplib.
        else:
            self._conditions, self._actions = [], []
            for i in range(16):
                if trigSection[i * 20 + 15] == 22:  # Always
                    continue
                elif trigSection[i * 20 + 15] >= 1:
                    self._conditions.append(Db(trigSection[i * 20 : i * 20 + 20]))
            self.preserved = bool(trigSection[320 + 2048] & 4)
            for i in range(64):
                if trigSection[320 + i * 32 + 26] == 3:  # PreserveTrigger
                    self.preserved = True
                elif trigSection[320 + i * 32 + 26] == 47:  # Comment
                    continue
                elif trigSection[320 + i * 32 + 26] >= 1:
                    action = Db(trigSection[320 + i * 32 : 320 + i * 32 + 32])
                    self._actions.append(action)

    def GetNextPtrMemory(self):
        return self + 4

    def GetDataSize(self):
        return 2408

    def CollectDependency(self, pbuffer):
        pbuffer.WriteDword(self._prevptr)
        pbuffer.WriteDword(self._nextptr)

        for cond in self._conditions:
            cond.CollectDependency(pbuffer)
        for act in self._actions:
            act.CollectDependency(pbuffer)

    def WritePayload(self, pbuffer):
        pbuffer.WriteDword(self._prevptr)
        pbuffer.WriteDword(self._nextptr)

        # Conditions
        for cond in self._conditions:
            cond.WritePayload(pbuffer)

        if len(self._conditions) != 16:
            pbuffer.WriteBytes(bytes(20))
            pbuffer.WriteSpace(20 * (15 - len(self._conditions)))

        # Actions
        for act in self._actions:
            act.WritePayload(pbuffer)

        if len(self._actions) != 64:
            pbuffer.WriteBytes(bytes(32))
            pbuffer.WriteSpace(32 * (63 - len(self._actions)))

        # Preserved flag

        if self.preserved:
            pbuffer.WriteDword(4)
        else:
            pbuffer.WriteDword(0)

        pbuffer.WriteSpace(27)
        pbuffer.WriteByte(0)
