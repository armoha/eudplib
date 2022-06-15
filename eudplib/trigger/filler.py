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
from ..core.eudfunc.eudf import _EUDPredefineParam

_lowordfilter = c.EUDXVariable(0, 0xFFFF)
_lsbytefilter = c.EUDXVariable(0, 0xFF)
_lobytefilter = c.EUDXVariable(0, 0xFF00)
_hibytefilter = c.EUDXVariable(0, 0xFF0000)
_msbytefilter = c.EUDXVariable(0, 0xFF000000)


def _filldw(dstepd, v1):
    c.SeqCompute(((dstepd, c.SetTo, v1),))


def _fillloword(dstepd, v1):
    c.VProc(
        [v1, _lowordfilter],
        [v1.QueueAssignTo(_lowordfilter), _lowordfilter.SetDest(dstepd)],
    )


def _filllsbyte(dstepd, v1):
    c.VProc(
        [v1, _lsbytefilter],
        [v1.QueueAssignTo(_lsbytefilter), _lsbytefilter.SetDest(dstepd)],
    )


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill_b__(v1):
    _lobytefilter << 0
    for i in ut.RandList(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_lobytefilter.AddNumber(2 ** (i + 8)),
        )


def _filllobyte(dstepd, v1):
    _fill_b__(v1)
    c.VProc(_lobytefilter, _lobytefilter.SetDest(dstepd))


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill__b_(v1):
    _hibytefilter << 0
    for i in ut.RandList(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_hibytefilter.AddNumber(2 ** (i + 16)),
        )


def _fillhibyte(dstepd, v1):
    _fill__b_(v1)
    c.VProc(_hibytefilter, _hibytefilter.SetDest(dstepd))


@_EUDPredefineParam(1)
@c.EUDFunc
def _fill___b(v1):
    _msbytefilter << 0
    for i in ut.RandList(range(8)):
        c.RawTrigger(
            conditions=v1.AtLeastX(1, 2**i),
            actions=_msbytefilter.AddNumber(2 ** (i + 24)),
        )


def _fillmsbyte(dstepd, v1):
    _fill___b(v1)
    c.VProc(_msbytefilter, _msbytefilter.SetDest(dstepd))
