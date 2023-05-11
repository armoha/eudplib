#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import utils as ut
from eudplib.localize import _

from .. import core as c
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener

"""
There are code duplication between EUDIf - EUDIfNot, EUDElseIf - EUDElseIfNot.
TODO : Remove code duplication if possible.
"""


def EUDIf():  # noqa: N802
    block = {
        "ifend": c.Forward(),
        "next_elseif": c.Forward(),
        "conditional": True,
    }
    ut.EUDCreateBlock("ifblock", block)

    def _footer(conditions, *, neg=False):
        if neg:
            EUDJumpIf(conditions, block["next_elseif"])
        else:
            EUDJumpIfNot(conditions, block["next_elseif"])
        block["conditional"] = False
        return True

    return CtrlStruOpener(_footer)


def EUDIfNot():  # noqa: N802
    c = EUDIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElseIf():  # noqa: N802
    def _header():
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None,
            _("Cannot have EUDElseIf after EUDElse"),
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


def EUDElseIfNot():  # noqa: N802
    c = EUDElseIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElse():  # noqa: N802
    def _footer():
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None,
            _("Cannot have EUDElse after EUDElse"),
        )

        # Finish previous if/elseif block
        EUDJump(block["ifend"])
        block["next_elseif"] << c.NextTrigger()
        block["next_elseif"] = None
        return True

    return CtrlStruOpener(_footer)


def EUDEndIf():  # noqa: N802
    lb = ut.EUDPopBlock("ifblock")
    block = lb[1]

    # Finalize
    nei_fw = block["next_elseif"]
    if nei_fw:
        nei_fw << c.NextTrigger()

    block["ifend"] << c.NextTrigger()


# -------


def EUDExecuteOnce():  # noqa: N802
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


def EUDEndExecuteOnce():  # noqa: N802
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
