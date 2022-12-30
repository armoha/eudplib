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

from ..localize import _
from .eperror import ep_assert


class BlockStruManager:
    def __init__(self):
        self._blockstru = []
        self._lastblockdict = {}

    def empty(self) -> bool:
        return not self._blockstru


_current_bsm = BlockStruManager()  # Default one


def SetCurrentBlockStruManager(bsm):
    global _current_bsm
    old_bsm = _current_bsm
    _current_bsm = bsm
    return old_bsm


def EUDCreateBlock(name, userdata) -> None:
    _blockstru = _current_bsm._blockstru
    _lastblockdict = _current_bsm._lastblockdict

    block = (name, userdata)
    _blockstru.append(block)

    if name not in _lastblockdict:
        _lastblockdict[name] = []
    _lastblockdict[name].append(block)


def EUDGetLastBlock():
    _blockstru = _current_bsm._blockstru
    return _blockstru[-1]


def EUDGetLastBlockOfName(name):
    _lastblockdict = _current_bsm._lastblockdict

    return _lastblockdict[name][-1]


def EUDPeekBlock(name):
    lastblock = EUDGetLastBlock()
    ep_assert(
        lastblock[0] == name,
        _("Block starting/ending mismatch")
        + ("\n" + _("    - Started with {}").format(lastblock[0]))
        + ("\n" + _("    - Ended with {}").format(name)),
    )
    return lastblock


def EUDPopBlock(name):
    _blockstru = _current_bsm._blockstru
    _lastblockdict = _current_bsm._lastblockdict

    lastblock = _blockstru.pop()
    ep_assert(
        lastblock[0] == name,
        _("Block starting/ending mismatch")
        + ("\n" + _("    - Started with {}").format(lastblock[0]))
        + ("\n" + _("    - Ended with {}").format(name)),
    )
    _lastblockdict[name].pop()
    return lastblock


def EUDGetBlockList():
    return _current_bsm._blockstru
