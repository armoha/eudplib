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

from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot


class EUDSCAnd:
    def __init__(self):
        self.const_cond = list()
        self.jb = c.Forward()
        self.v = c.EUDLightVariable()
        self.v << 1

        if c.PushTriggerScope():
            self.fb = c.RawTrigger(nextptr=self.jb, actions=self.v.SetNumber(0))
        c.PopTriggerScope()

    def __call__(self, cond=None, *, neg=False):
        if cond is None:
            if self.const_cond:
                EUDJumpIfNot(self.const_cond, self.fb)
                self.const_cond.clear()
            self.jb << c.NextTrigger()
            return self.v.AtLeast(1)

        else:
            if neg:
                if self.const_cond:
                    EUDJumpIfNot(self.const_cond, self.fb)
                    self.const_cond.clear()
                EUDJumpIf(cond, self.fb)
            else:
                self.const_cond.append(cond)
                try:
                    cond.CheckArgs(0)
                except ut.EPError as e:
                    EUDJumpIfNot(self.const_cond, self.fb)
                    self.const_cond.clear()
            return self


class EUDSCOr:
    def __init__(self):
        self.jb = c.Forward()
        self.v = c.EUDVariable()
        self.v << 0

        if c.PushTriggerScope():
            self.tb = c.RawTrigger(nextptr=self.jb, actions=self.v.SetNumber(1))
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
