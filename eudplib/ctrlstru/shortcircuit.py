#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import trigger as tg
from .. import utils as ut
from .basicstru import EUDJumpIf, EUDJumpIfNot


class EUDSCAnd:
    def __init__(self):
        self.const = True
        self.cond = list()
        c.PushTriggerScope()
        self.side_effect = c.NextTrigger()
        self.scope = ut.EUDGetLastBlock()

    def Patch(self):
        self.const = False
        self.jb = c.Forward()
        try:
            is_conditional = self.scope[1]["conditional"]
        except KeyError:
            is_conditional = False
        if is_conditional:
            self.v = c.EUDLightBool()
            self.fb = c.RawTrigger(nextptr=self.jb, actions=self.v.Clear())
            c.PopTriggerScope()
            c.RawTrigger(actions=self.v.Set())
        else:
            self.v = c.EUDVariable()
            self.fb = c.RawTrigger(nextptr=self.jb, actions=self.v.SetNumber(0))
            c.PopTriggerScope()
            self.v << True

    def __call__(self, cond=None, *, neg=False):
        if cond is None:
            if self.const:
                c.PopTriggerScope()
                return self.cond
            elif self.cond:
                EUDJumpIfNot(self.cond, self.fb)
            self.jb << c.NextTrigger()
            return self.v

        if not self.const:
            if neg:
                EUDJumpIf(cond, self.fb)
            else:
                EUDJumpIfNot(cond, self.fb)
        else:
            is_const_cond = tg.tpatcher.IsConditionConst(cond)
            nt_list = self.scope[1]["nexttrigger_list"]
            if nt_list != [self.side_effect]:
                # has side-effect
                ifcond = c.Forward()
                c.SetNextTrigger(ifcond)
                self.Patch()
                if self.cond:
                    EUDJumpIfNot(self.cond, self.fb)
                    self.cond.clear()
                c.SetNextTrigger(self.side_effect)
                ifcond << c.NextTrigger()
                if neg:
                    EUDJumpIf(cond, self.fb)
                else:
                    EUDJumpIfNot(cond, self.fb)
            elif is_const_cond:
                if neg:
                    if tg.tpatcher.IsConditionNegatable(cond):
                        cond = tg.tpatcher.NegateCondition(cond)
                        self.cond.append(cond)
                    else:
                        self.Patch()
                        if self.cond:
                            EUDJumpIfNot(self.cond, self.fb)
                            self.cond.clear()
                        EUDJumpIf(cond, self.fb)
                else:
                    self.cond.append(cond)
            else:
                self.Patch()
                # TODO: handle mixing of non/side-effect conditions
                if self.cond:
                    EUDJumpIfNot(self.cond, self.fb)
                    self.cond.clear()
                if neg:
                    EUDJumpIf(cond, self.fb)
                else:
                    EUDJumpIfNot(cond, self.fb)
        return self


class EUDSCOr:
    def __init__(self):
        self.jb = c.Forward()
        self.v = c.EUDLightBool()
        c.RawTrigger(actions=self.v.Clear())

        if c.PushTriggerScope():
            self.tb = c.RawTrigger(nextptr=self.jb, actions=self.v.Set())
        c.PopTriggerScope()

    def __call__(self, cond=None, *, neg=False):
        if cond is None:
            self.jb << c.NextTrigger()
            return self.v

        else:
            if neg:
                EUDJumpIfNot(cond, self.tb)
            else:
                EUDJumpIf(cond, self.tb)
            return self
