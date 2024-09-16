# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal, TypedDict

from .. import core as c
from .. import utils as ut
from ..localize import _
from .basicstru import EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener

"""
There are code duplication between EUDIf - EUDIfNot, EUDElseIf - EUDElseIfNot.
TODO : Remove code duplication if possible.
"""


def EUDIf() -> CtrlStruOpener:  # noqa: N802
    block = {
        "ifend": c.Forward(),
        "next_elseif": c.Forward(),
        "conditional": True,
    }
    ut.EUDCreateBlock("ifblock", block)

    def _footer(conditions, *, neg=False) -> Literal[True]:
        if neg:
            EUDJumpIf(conditions, block["next_elseif"])
        else:
            EUDJumpIfNot(conditions, block["next_elseif"])
        block["conditional"] = False
        return True

    return CtrlStruOpener(_footer)


def EUDIfNot() -> CtrlStruOpener:  # noqa: N802
    c = EUDIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElseIf() -> CtrlStruOpener:  # noqa: N802
    def _header() -> None:
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None,
            _("Cannot have EUDElseIf after EUDElse"),
        )

        # Finish previous if/elseif block
        c.SetNextTrigger(block["ifend"])

        block["next_elseif"] << c.NextTrigger()
        block["next_elseif"] = c.Forward()
        block["conditional"] = True

    def _footer(conditions, *, neg=False) -> Literal[True]:
        block = ut.EUDPeekBlock("ifblock")[1]
        if neg:
            EUDJumpIf(conditions, block["next_elseif"])
        else:
            EUDJumpIfNot(conditions, block["next_elseif"])
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDElseIfNot() -> CtrlStruOpener:  # noqa: N802
    c = EUDElseIf()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


# -------


def EUDElse() -> CtrlStruOpener:  # noqa: N802
    def _footer() -> Literal[True]:
        block = ut.EUDPeekBlock("ifblock")[1]
        ut.ep_assert(
            block["next_elseif"] is not None,
            _("Cannot have EUDElse after EUDElse"),
        )

        # Finish previous if/elseif block
        c.SetNextTrigger(block["ifend"])
        block["next_elseif"] << c.NextTrigger()
        block["next_elseif"] = None
        return True

    return CtrlStruOpener(_footer)


def EUDEndIf() -> None:  # noqa: N802
    lb = ut.EUDPopBlock("ifblock")
    block = lb[1]

    # Finalize
    nei_fw = block["next_elseif"]
    if nei_fw:
        nei_fw << c.NextTrigger()

    block["ifend"] << c.NextTrigger()


# -------


def EUDExecuteOnce() -> CtrlStruOpener:  # noqa: N802
    def _header() -> None:
        class OnceBlock(TypedDict):
            blockstart: c.Forward
            blockend: c.Forward
            blockmode: bool
            conditional: bool

        block: OnceBlock = {
            "blockstart": c.Forward(),
            "blockend": c.Forward(),
            "blockmode": False,
            "conditional": True,
        }
        ut.EUDCreateBlock("executeonceblock", block)
        block["blockstart"] << c.NextTrigger()

    def _footer(conditions=None, *, neg=False) -> Literal[True]:
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


def EUDEndExecuteOnce() -> None:  # noqa: N802
    lb = ut.EUDPopBlock("executeonceblock")
    ut.ep_assert(lb[0] == "executeonceblock", _("Block start/end mismatch"))
    block = lb[1]
    if not block["blockmode"]:
        c.RawTrigger(
            actions=[
                c.SetNextPtr(block["blockstart"], block["blockend"]),
                c.SetMemory(block["blockstart"] + 2376, c.SetTo, 8),
            ]
        )
    block["blockend"] << c.NextTrigger()
