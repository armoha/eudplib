# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Any

from ..localize import _
from .eperror import EPError, TriggerScopeError, ep_assert

block = tuple[str, Any]


class BlockStruManager:
    def __init__(self) -> None:
        self._blockstru: list[block] = []
        self._lastblockdict: dict[str, list[block]] = {}

    def empty(self) -> bool:
        return not self._blockstru


_current_bsm = BlockStruManager()  # Default one


def set_blockstru_manager(bsm: BlockStruManager) -> BlockStruManager:
    global _current_bsm
    old_bsm = _current_bsm
    _current_bsm = bsm
    return old_bsm


def EUDCreateBlock(name: str, userdata: Any) -> None:  # noqa: N802
    _blockstru = _current_bsm._blockstru
    _lastblockdict = _current_bsm._lastblockdict

    block = (name, userdata)
    _blockstru.append(block)

    if name not in _lastblockdict:
        _lastblockdict[name] = []
    _lastblockdict[name].append(block)


def EUDGetLastBlock() -> block:  # noqa: N802
    _blockstru = _current_bsm._blockstru
    return _blockstru[-1]


def EUDGetLastBlockOfName(name: str) -> block:  # noqa: N802
    _lastblockdict = _current_bsm._lastblockdict
    try:
        return _lastblockdict[name][-1]
    except (IndexError, KeyError):
        if name == "triggerscope":
            raise TriggerScopeError()
        raise EPError(_("Block not found: {}").format(name))


def EUDPeekBlock(name: str) -> block:  # noqa: N802
    lastblock = EUDGetLastBlock()
    ep_assert(
        lastblock[0] == name,
        _("Block starting/ending mismatch")
        + ("\n" + _("    - Started with {}").format(lastblock[0]))
        + ("\n" + _("    - Ended with {}").format(name)),
    )
    return lastblock


def EUDPopBlock(name: str) -> block:  # noqa: N802
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


def EUDGetBlockList() -> list[block]:  # noqa: N802
    return _current_bsm._blockstru
