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

from .. import core as c, trigger as tg, utils as ut

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
        self.v = c.EUDLightBool()
        self.fb = c.RawTrigger(nextptr=self.jb, actions=self.v.Clear())
        c.PopTriggerScope()
        c.RawTrigger(actions=self.v.Set())

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
