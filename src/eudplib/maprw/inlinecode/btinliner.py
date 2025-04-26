# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import ByteString, Collection
from typing import TypeAlias

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...trigtrg.runtrigtrg import _runner_cp

_shared_triggers: list[bytes | c.RawTrigger] = []
t_start_end: TypeAlias = tuple[c.ConstExpr, c.RawTrigger]


def get_executing_players(
    btrigger: bytes,
) -> list[bool]:
    # Get executing players of the trigger.
    # If AllPlayers executes it, then pass it
    if btrigger[320 + 2048 + 4 + 17] != 0:
        return [True] * 8
    # Should check manually, by player and force
    return [
        (
            bool(btrigger[320 + 2048 + 4 + player])
            or bool(btrigger[320 + 2048 + 4 + 18 + c.GetPlayerInfo(player).force])
        )
        for player in range(8)
    ]


def _preserved_and_has_no_wait(btrigger: ByteString) -> bool:
    exec_once = True
    for i in range(64):
        actionflag = btrigger[320 + 32 * i + 28]
        if not actionflag & 0b10:  # Enabled Flag
            continue
        actionbyte = btrigger[320 + 32 * i + 26]
        if actionbyte in (4, 7):  # Wait or Transmission
            return False
        elif actionbyte == 3:  # PreserveTrigger
            exec_once = False
    if exec_once and not (btrigger[320 + 2048] & 4):
        return False
    return True


def inline_codify_binary_trigger(btrigger: bytes) -> t_start_end:
    """Inline codify raw(binary) trigger data.

    For minimal protection, eudplib make some of the trig-triggers to
    eudplib trigger. This function makes eudplib trigger out of raw
    binary trigger stream.

    :param btrigger: Binary trigger data
    :returns: (tstart, tend) pair, as being used by tend
    """

    # 1. Get executing players of the trigger.
    # If all player executes it, then pass it
    executing_players = get_executing_players(btrigger)

    # 2. Create function body

    if c.PushTriggerScope():
        tstart = c.RawTrigger(actions=c.SetDeaths(0, c.SetTo, 0, 0))

        cp = _runner_cp
        execp = [p for p, e in enumerate(executing_players) if e]
        no_wait_and_preserved = _preserved_and_has_no_wait(btrigger)

        if no_wait_and_preserved and len(execp) == 8:
            tend = c.RawTrigger(trigSection=btrigger)
        if no_wait_and_preserved and max(execp) - min(execp) == len(execp) - 1:
            if cs.EUDIf()([cp >= min(execp), cp <= max(execp)]):
                c.RawTrigger(trigSection=btrigger)
            cs.EUDEndIf()
            tend = c.RawTrigger()
        else:
            cs.EUDSwitch(cp)
            for player in range(8):
                if executing_players[player]:
                    if cs.EUDSwitchCase()(player):
                        c.RawTrigger(trigSection=btrigger)
                        cs.EUDBreak()

            cs.EUDEndSwitch()

            tend = c.RawTrigger()
    c.PopTriggerScope()

    return tstart, tend


def _count_conditions_and_actions(btrigger: bytes) -> tuple[int, int]:
    cond_count, act_count = 0, 0
    for cond in range(16):
        if btrigger[cond * 20 + 15] == 22:  # Always
            continue
        elif btrigger[cond * 20 + 15] >= 1:
            cond_count += 1
    for act in range(64):
        if btrigger[320 + act * 32 + 26] in (47,):  # Comment
            continue
        elif btrigger[320 + act * 32 + 26] >= 1:
            act_count += 1
    return cond_count, act_count


def get_trigger_size(btrigger: bytes) -> int:
    cond_count, act_count = _count_conditions_and_actions(btrigger)
    min_size = 4 + 5 * cond_count + 8 * act_count
    trig = {
        "n": [1],  # nextptr
        "P": [594],  # preserved
        "C": list(range(2, 2 + 5 * cond_count)),  # conditions
        "c": [5 + 5 * cond_count],  # condtype == 0
        "A": list(range(82, 82 + 8 * act_count)),  # actions
        "a": [88 + 8 * act_count],  # acttype == 0
    }
    if cond_count == 16:
        del trig["c"]
    if act_count == 64:
        del trig["a"]

    for ret in range(min_size, 2408 // 4):
        output = ["_" for _ in range(ret)]

        def _f():
            for k, v in trig.items():
                for x in v:
                    if output[x % ret] != "_":
                        return False
                    output[x % ret] = k
            return True

        if _f():
            return ret * 4
    return 2408


def try_share_trigger(btrigger: bytes) -> int | bytes:
    if _preserved_and_has_no_wait(btrigger):
        _shared_triggers.append(btrigger)
        return len(_shared_triggers) - 1
    return btrigger


def inline_codify_binary_triggers(
    btriggers: Collection[bytes | int],
) -> t_start_end:
    """Inline codify raw(binary) trigger data.

    For minimal protection, eudplib make some of the trig-triggers to
    eudplib trigger. This function makes eudplib trigger out of raw
    binary trigger stream.

    :param btrigger: Binary trigger data
    :returns: (tstart, tend) pair, as being used by tend
    """

    # Create function body

    first_trigger = None
    t_startactions = [c.SetDeaths(0, c.SetTo, 0, 0)]
    b2s = False

    if c.PushTriggerScope():
        next_trigger = c.Forward()
        for i, btrigger in enumerate(btriggers):
            tend: c.RawTrigger
            if isinstance(btrigger, bytes):
                tend = c.RawTrigger(trigSection=btrigger)
                next_trigger << tend
                if i < len(btriggers) - 1:
                    next_trigger = c.Forward()
                b2s = True
            elif isinstance(btrigger, int):
                shared_trigger = _shared_triggers[btrigger]
                if isinstance(shared_trigger, bytes):
                    tend = c.RawTrigger(trigSection=shared_trigger)
                    _shared_triggers[btrigger] = tend
                elif isinstance(shared_trigger, c.RawTrigger):
                    tend = shared_trigger
                    if b2s:
                        c.SetNextTrigger(shared_trigger)
                else:
                    raise TypeError()
                next_trigger << tend
                if i < len(btriggers) - 1:
                    next_trigger = c.Forward()
                    t_startactions.append(c.SetNextPtr(tend, next_trigger))
                b2s = False
            else:
                raise TypeError()
            if first_trigger is None:
                first_trigger = tend
    c.PopTriggerScope()

    if first_trigger is None:
        raise TypeError()

    if c.PushTriggerScope():
        tstart = c.Forward()
        tstart << c.NextTrigger()

        cs.DoActions(t_startactions)

        c.SetNextTrigger(first_trigger)

    c.PopTriggerScope()

    return tstart, tend
