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
from eudplib import utils as ut
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener
from eudplib.localize import _


"""
There are code duplication between EUDIf - EUDIfNot, EUDElseIf - EUDElseIfNot.
TODO : Remove code duplication if possible.
"""


def EUDIf():
    block = {"ifend": c.Forward(), "next_elseif": c.Forward(), "conditional": True}
    ut.EUDCreateBlock("ifblock", block)

    def _footer(conditions, *, neg=False):
        if neg:
            EUDJumpIf(conditions, block["next_elseif"])
        else:
            EUDJumpIfNot(conditions, block["next_elseif"])
        block["conditional"] = False
        return True

    return CtrlStruOpener(_footer)


def EUDIfNot():
    c = EUDIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElseIf():
    def _header():
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None, _("Cannot have EUDElseIf after EUDElse")
        )

        # Finish previous if/elseif block
        EUDJump(block["ifend"])

        block["next_elseif"] << c.NextTrigger()
        block["next_elseif"] = c.Forward()
        block["conditional"] = True

    def _footer(conditions, *, neg=False):
        block = ut.EUDPeekBlock("ifblock")[1]
        if neg:
            EUDJumpIf(conditions, block["next_elseif"])
        else:
            EUDJumpIfNot(conditions, block["next_elseif"])
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDElseIfNot():
    c = EUDElseIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElse():
    def _footer():
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None, _("Cannot have EUDElse after EUDElse")
        )

        # Finish previous if/elseif block
        EUDJump(block["ifend"])
        block["next_elseif"] << c.NextTrigger()
        block["next_elseif"] = None
        return True

    return CtrlStruOpener(_footer)


def EUDEndIf():
    lb = ut.EUDPopBlock("ifblock")
    block = lb[1]

    # Finalize
    nei_fw = block["next_elseif"]
    if nei_fw:
        nei_fw << c.NextTrigger()

    block["ifend"] << c.NextTrigger()


# -------


def EUDExecuteOnce():
    def _header():
        block = {
            "blockstart": c.Forward(),
            "blockend": c.Forward(),
            "blockmode": None,
            "conditional": True,
        }
        ut.EUDCreateBlock("executeonceblock", block)
        block["blockstart"] << c.NextTrigger()

    def _footer(conditions=None, *, neg=False):
        block = ut.EUDPeekBlock("executeonceblock")[1]
        if conditions is not None:
            if neg:
                block["blockmode"] = False
                EUDJumpIf(conditions, block["blockend"])
            else:
                block["blockmode"] = True
                skip = [
                    c.SetNextPtr(block["blockstart"], block["blockend"]),
                    c.SetMemory(block["blockstart"] + 2376, c.SetTo, 8),
                ]
                EUDJumpIfNot(conditions, block["blockend"], _actions=skip)
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDEndExecuteOnce():
    lb = ut.EUDPopBlock("executeonceblock")
    ut.ep_assert(lb[0] == "executeonceblock", _("Block start/end mismatch"))
    block = lb[1]
    if (block["blockmode"] is None) or (block["blockmode"] is False):
        c.RawTrigger(
            actions=[
                c.SetNextPtr(block["blockstart"], block["blockend"]),
                c.SetMemory(block["blockstart"] + 2376, c.SetTo, 8),
            ]
        )
    block["blockend"] << c.NextTrigger()
