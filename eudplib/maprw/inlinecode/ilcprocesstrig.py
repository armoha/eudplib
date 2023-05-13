#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from random import random

from ... import utils as ut
from ...core.mapdata.chktok import CHK
from ...core.rawtrigger import AllPlayers, SetTo
from ...trigtrg import trigtrg as tt
from .btInliner import (
    GetExecutingPlayers,
    GetTriggerSize,
    InlineCodifyBinaryTrigger,
    InlineCodifyMultipleBinaryTriggers,
    TryToShareTrigger,
    tStartEnd,
)
from .ilccompile import _compile_inline_code, ComputeBaseInlineCodeGlobals

_inline_codes: list[tuple[int, tStartEnd]] = []
_inlining_rate: float = 1.0
_cutoff_rate: list[float] = [1 + (i - 2) / 3 for i in range(9)]


def PRT_SetInliningRate(rate: float) -> None:  # noqa: N802
    """Set how much triggers will be inlined into STR section."""
    global _inlining_rate
    _inlining_rate = rate


def _preprocess_inline_code(chkt: CHK) -> None:
    global _inline_codes
    trig_section = chkt.getsection("TRIG")
    _inline_codes, trig_section = _preprocess_trig_section(trig_section)
    chkt.setsection("TRIG", trig_section)


def _preprocess_trig_section(
    trig_section: bytes
) -> tuple[list[tuple[int, tStartEnd]], bytes]:
    """Fetch inline codes & compiles them"""
    ComputeBaseInlineCodeGlobals()
    if _inlining_rate >= 1.0:
        return _consecutive_inline_trig_section(trig_section)

    inline_codes: list[tuple[int, tStartEnd]] = []
    trig_segments: list[bytes] = []
    for i in range(0, len(trig_section), 2400):
        trig_segment = trig_section[i : i + 2400]
        if len(trig_segment) != 2400:
            continue

        propv = ut.b2i4(trig_segment, 320 + 2048)

        decoded = _dispatch_inline_code(inline_codes, trig_segment)
        if decoded:
            trig_segment = decoded

        elif propv < 0x80000000 and random() < _inlining_rate:
            trig_segment = _inlinify_normal_trigger(inline_codes, trig_segment)

        trig_segments.append(trig_segment)

    """
    This is rather hard to explain, but we need blank trigger.

    If inline_eudplib trigger is at the last of the trigger, then its
    nextptr should be modified to codeStart.

    But after flipprop works, RunTrigTrigger engine will re-change its nextptr
    to somewhere else, where everything quits.

    So we need 'normal' trigger at the last of TRIG triggers for every player.
    """
    trig_segments.append(tt.Trigger(players=[AllPlayers]))

    trig_section = b"".join(trig_segments)
    return inline_codes, trig_section


def _consecutive_inline_trig_section(
    trig_section: bytes,
) -> tuple[list[tuple[int, tStartEnd]], bytes]:
    inline_codes: list[tuple[int, tStartEnd]] = []
    trig_segments: list[bytes] = []
    ptriggers: list[list[bytes]] = [[] for _ in range(8)]

    def append_ptriggers(p):
        if ptriggers[p]:
            func = InlineCodifyMultipleBinaryTriggers(ptriggers[p])
            trig_segment = _create_inline_code_dispatcher(
                inline_codes, func, 1 << p
            )
            trig_segments.append(trig_segment)
            ptriggers[p].clear()

    for i in range(0, len(trig_section), 2400):
        trig_segment = trig_section[i : i + 2400]
        if len(trig_segment) != 2400:
            continue

        propv = ut.b2i4(trig_segment, 320 + 2048)
        executing_players = GetExecutingPlayers(trig_segment)

        decoded = _dispatch_inline_code(inline_codes, trig_segment)
        if decoded:
            trig_segment = decoded

        elif propv < 0x80000000:
            player_count = executing_players.count(True)
            if player_count >= 2:
                index_or_trig = TryToShareTrigger(trig_segment)
                if isinstance(index_or_trig, bytes):
                    size = GetTriggerSize(index_or_trig)
                    if size * player_count * _cutoff_rate[player_count] > 2400:
                        for p in range(8):
                            if executing_players[p]:
                                append_ptriggers(p)
                        trig_segments.append(index_or_trig)
                        continue
            for p in range(8):
                if executing_players[p]:
                    ptriggers[p].append(trig_segment)
            continue
        for p in range(8):
            if executing_players[p]:
                append_ptriggers(p)
        trig_segments.append(trig_segment)
    for p in range(8):
        append_ptriggers(p)
    trig_segments.append(tt.Trigger(players=[AllPlayers]))

    trig_section = b"".join(trig_segments)
    return inline_codes, trig_section


def _get_inline_code_list() -> list[tuple[int, tStartEnd]]:
    """Get list of compiled inline_eudplib code"""
    return _inline_codes


def _get_inline_code_player_list(btrigger: bytes) -> int | None:
    # Check if effplayer & current_action is empty
    for player in range(28):
        if btrigger[320 + 2048 + 4 + player] != 0:
            return None

    # trg.cond[0].condtype != 0
    if btrigger[15] != 0:
        return None
    # trg.act[0].acttype != 0
    if btrigger[346] != 0:
        return None

    return ut.b2i4(btrigger, 24)


def _dispatch_inline_code(
    inline_codes: list[tuple[int, tStartEnd]], trigger_bytes: bytes
) -> bytearray | None:
    """Check if trigger segment has special data."""
    magic_code = ut.b2i4(trigger_bytes, 20)
    if magic_code != 0x10978D4A:
        return None

    player_code = _get_inline_code_player_list(trigger_bytes)
    if not player_code:
        return None

    data = trigger_bytes[20:320] + trigger_bytes[352:2372]
    code_data = ut.b2u(data[8:]).rstrip("\0")

    # Compile code
    func = _compile_inline_code(code_data)
    return _create_inline_code_dispatcher(inline_codes, func, player_code)


def _inlinify_normal_trigger(
    inline_codes: list[tuple[int, tStartEnd]], trigger_bytes: bytes
) -> bytearray:
    """Inlinify normal binary triggers"""
    player_code = 0
    for i in range(27):
        if trigger_bytes[320 + 2048 + 4 + i]:
            player_code |= 1 << i

    func = InlineCodifyBinaryTrigger(trigger_bytes)
    return _create_inline_code_dispatcher(inline_codes, func, player_code)


def _create_inline_code_dispatcher(
    inline_codes: list[tuple[int, tStartEnd]],
    func: tStartEnd,
    player_code: int,
) -> bytearray:
    """Create link from TRIG list to STR trigger."""
    func_id = len(inline_codes) + 1024
    inline_codes.append((func_id, func))

    # Return new trigger
    new_trigger = bytearray(2400)

    # Apply effplayer
    for player in range(27):
        if player_code & (1 << player):
            new_trigger[320 + 2048 + 4 + player] = 1

    # Apply 4 SetDeaths
    setdeaths_template = tt.SetDeaths(0, SetTo, 0, 0)
    new_trigger[320 + 32 * 0 : 320 + 32 * 1] = setdeaths_template
    new_trigger[320 + 32 * 1 : 320 + 32 * 2] = setdeaths_template
    new_trigger[320 + 32 * 2 : 320 + 32 * 3] = setdeaths_template
    new_trigger[320 + 32 * 3 : 320 + 32 * 4] = setdeaths_template

    # Apply flag
    new_trigger[0:4] = ut.i2b4(func_id)
    new_trigger[2368:2372] = b"\0\0\0\x10"

    return new_trigger
