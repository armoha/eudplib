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
from .. import utils as ut

_lowordfilter = c.EUDXVariable(0, 0xFFFF)
_lsbytefilter = c.EUDXVariable(0, 0xFF)
_lobytefilter = c.EUDXVariable(0, 0xFF00)
_hibytefilter = c.EUDXVariable(0, 0xFF0000)
_msbytefilter = c.EUDXVariable(0, 0xFF000000)


def _filldw(dstepd, v1):
    c.SeqCompute(((dstepd, c.SetTo, v1),))


def _fillloword(dstepd, v1):
    _nextptr = c.Forward()
    c.RawTrigger(
        nextptr=v1.GetVTable(),
        actions=[
            v1.QueueAssignTo(_lowordfilter),
            c.SetNextPtr(v1.GetVTable(), _lowordfilter.GetVTable()),
            _lowordfilter.QueueAssignTo(dstepd),
            c.SetNextPtr(_lowordfilter.GetVTable(), _nextptr),
        ]
    )
    _nextptr << c.NextTrigger()


def _filllsbyte(dstepd, v1):
    _nextptr = c.Forward()
    c.RawTrigger(
        nextptr=v1.GetVTable(),
        actions=[
            v1.QueueAssignTo(_lsbytefilter),
            c.SetNextPtr(v1.GetVTable(), _lsbytefilter.GetVTable()),
            _lsbytefilter.QueueAssignTo(dstepd),
            c.SetNextPtr(_lsbytefilter.GetVTable(), _nextptr),
        ]
    )
    _nextptr << c.NextTrigger()


@c.EUDFunc
def _fill_b__(v1):
    global _lobytefilter
    _lobytefilter << 0
    for i in range(7, -1, -1):
        c.RawTrigger(
            conditions=v2.AtLeastX(1, 2 ** i),
            actions=_lobytefilter.AddNumber(2 ** (i + 8)),
        )


def _filllobyte(dstepd, v1):
    _fill_b__(v1)
    c.SeqCompute(((dstepd, c.SetTo, _lobytefilter),))


@c.EUDFunc
def _fill__b_(v1):
    global _hibytefilter
    _hibytefilter << 0
    for i in range(7, -1, -1):
        c.RawTrigger(
            conditions=v2.AtLeastX(1, 2 ** i),
            actions=_hibytefilter.AddNumber(2 ** (i + 16)),
        )


def _fillhibyte(dstepd, v1):
    _fill__b_(v1)
    c.SeqCompute(((dstepd, c.SetTo, _hibytefilter),))


@c.EUDFunc
def _fill___b(v1):
    global _msbytefilter
    _msbytefilter << 0
    for i in range(7, -1, -1):
        c.RawTrigger(
            conditions=v2.AtLeastX(1, 2 ** i),
            actions=_msbytefilter.AddNumber(2 ** (i + 24)),
        )


def _fillmsbyte(dstepd, v1):
    _fill___b(v1)
    c.SeqCompute(((dstepd, c.SetTo, _msbytefilter),))
