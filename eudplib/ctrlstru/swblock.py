#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from itertools import chain, combinations

from eudplib import utils as ut
from eudplib.localize import _

from .. import core as c
from .. import trigger as tg
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener
from .jumptable import JumpTriggerForward


def _is_switch_blockid(idf):
    return idf == "swblock"


def EPDSwitch(epd, mask=0xFFFFFFFF):  # noqa: N802
    epd = c.EncodePlayer(epd)
    epd = ut.unProxy(epd)
    block = {
        "targetepd": epd,
        "bitmask": mask,
        "casebrlist": {},
        "defaultbr": c.Forward(),
        "swend": c.Forward(),
    }

    c.PushTriggerScope()
    ut.EUDCreateBlock("swblock", block)

    return True


def EUDSwitch(var, mask=0xFFFFFFFF):  # noqa: N802
    var = ut.unProxy(var)
    block = {
        "targetvar": var,
        "bitmask": mask,
        "casebrlist": {},
        "defaultbr": c.Forward(),
        "swend": c.Forward(),
    }

    c.PushTriggerScope()
    ut.EUDCreateBlock("swblock", block)

    return True


def EUDSwitchCase():  # noqa: N802
    def _footer(*numbers):
        for number in numbers:
            ut.ep_assert(
                isinstance(number, int) or isinstance(number, c.ConstExpr),
                _("Invalid selector start for EUDSwitch"),
            )

        lb = ut.EUDGetLastBlock()
        ut.ep_assert(lb[0] == "swblock", _("Block start/end mismatch"))
        block = lb[1]

        for number in numbers:
            case = number & block["bitmask"]
            ut.ep_assert(case not in block["casebrlist"], _("Duplicate cases"))
            ut.ep_assert(
                block["bitmask"] == 0xFFFFFFFF or case == number,
                _("cases out of mask"),
            )
            block["casebrlist"][case] = c.NextTrigger()

        return True

    return CtrlStruOpener(_footer)


def EUDSwitchDefault():  # noqa: N802
    def _footer():
        lb = ut.EUDGetLastBlock()
        ut.ep_assert(lb[0] == "swblock", _("Block start/end mismatch"))
        block = lb[1]

        ut.ep_assert(not block["defaultbr"].IsSet(), _("Duplicate default"))
        block["defaultbr"] << c.NextTrigger()

        return True

    return CtrlStruOpener(_footer)


def eudswitch_break():
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJump(block["swend"])


def eudswitch_break_if(conditions):
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJumpIf(conditions, block["swend"])


def eudswitch_break_ifnot(conditions):
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJumpIfNot(conditions, block["swend"])


def EUDEndSwitch():  # noqa: N802
    lb = ut.EUDPopBlock("swblock")
    block = lb[1]
    swend = block["swend"]
    EUDJump(swend)  # Exit switch block
    c.PopTriggerScope()

    bitmask = block["bitmask"]
    casebrlist = block["casebrlist"]
    defbranch = block["defaultbr"]
    casekeylist = sorted(block["casebrlist"].keys())

    # If default block is not specified, skip it.
    if not defbranch.IsSet():
        defbranch << swend

    # If there is only the default destination, jump there directly.
    if not casekeylist:
        c.SetNextTrigger(defbranch)
        swend << c.NextTrigger()
        return

    try:
        epd = ut.EPD(block["targetvar"].getValueAddr())
    except KeyError:
        epd = block["targetepd"]
    except AttributeError:
        # constant value switch
        if block["targetvar"] in casekeylist:
            c.SetNextTrigger(casebrlist[block["targetvar"]])
        else:
            c.SetNextTrigger(defbranch)
        swend << c.NextTrigger()
        return

    if (
        len(casekeylist) == 2
        and casebrlist[casekeylist[0]] == casebrlist[casekeylist[1]]
    ):

        def popcount(x):
            x -= (x >> 1) & 0x55555555
            x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
            x = (x + (x >> 4)) & 0x0F0F0F0F
            x += x >> 8
            x += x >> 16
            return x & 0x0000003F

        keyand = casekeylist[0] & casekeylist[1]
        keyxor = (casekeylist[0] | casekeylist[1]) - keyand
        if popcount(keyxor) == 1:
            tg.EUDBranch(
                c.MemoryXEPD(epd, c.Exactly, keyand, ~keyxor & bitmask),
                casebrlist[casekeylist[0]],
                defbranch,
            )
            swend << c.NextTrigger()
            return

    if len(casekeylist) <= 3 and not c.IsEUDVariable(epd):
        # use simple comparisons
        branch, nextbranch = c.Forward(), c.Forward()
        restore = c.SetMemory(branch + 4, c.SetTo, nextbranch)
        c.RawTrigger(
            actions=[restore, block["_actions"]]
            if "_actions" in block
            else restore
        )
        for case in casekeylist:
            branch << c.RawTrigger(
                conditions=c.MemoryXEPD(epd, c.Exactly, case, bitmask),
                actions=[
                    c.SetNextPtr(branch, casebrlist[case]),
                    c.SetMemory(restore + 16, c.SetTo, ut.EPD(branch) + 1),
                    c.SetMemory(restore + 20, c.SetTo, nextbranch),
                ],
            )
            nextbranch << c.NextTrigger()
            branch, nextbranch = c.Forward(), c.Forward()
        c.SetNextTrigger(defbranch)
        swend << c.NextTrigger()
        return

    keyand, keyor = casekeylist[0], 0
    for key in casekeylist:
        keyand &= key
        keyor |= key
    keyxor = keyor - keyand
    keybits = list(ut.bits(keyxor))

    density = len(casebrlist) / (2 ** len(keybits))
    if density >= 0.4:
        # use jump table
        if (~keyor | keyand) & bitmask != 0:
            check_invariant = c.MemoryXEPD(
                epd, c.Exactly, keyand, (~keyor | keyand) & bitmask
            )
            EUDJumpIfNot(check_invariant, defbranch)

        def powerset(iterable):
            "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
            s = list(iterable)
            return chain.from_iterable(
                combinations(s, r) for r in range(len(s) + 1)
            )

        keylist = sorted(map(sum, powerset(keybits)))
        jump_table = JumpTriggerForward(
            [casebrlist.get(keyand + key, defbranch) for key in keylist]
        )
        jumper = c.Forward()

        cmpplayer = epd
        if c.IsEUDVariable(epd):
            cmpplayer = c.EncodePlayer(c.CurrentPlayer)
            cpcache = c.curpl.GetCPCache()
            c.VProc(
                epd,
                [
                    cpcache.SetDest(ut.EPD(0x6509B0)),
                    epd.QueueAssignTo(ut.EPD(0x6509B0)),
                    c.SetNextPtr(jumper, jump_table),
                    block["_actions"] if "_actions" in block else [],
                ],
            )
        else:
            restore = c.SetNextPtr(jumper, jump_table)
            lastbit = c.RawTrigger(
                actions=[restore, block["_actions"]]
                if "_actions" in block
                else restore
            )

        for i, bit in enumerate(keybits):
            lastbit = c.RawTrigger(
                conditions=c.MemoryXEPD(cmpplayer, c.AtLeast, 1, bit),
                actions=c.SetMemory(jumper + 4, c.Add, 20 * (1 << i)),
            )

        if c.IsEUDVariable(epd):
            jumper << cpcache.GetVTable()
            c.SetNextTrigger(cpcache.GetVTable())
        else:
            jumper << lastbit
    elif c.IsEUDVariable(epd):
        # use binary search with CP trick
        cmpplayer = c.EncodePlayer(c.CurrentPlayer)
        cpcache = c.curpl.GetCPCache()
        c.VProc(
            epd,
            [
                cpcache.SetDest(ut.EPD(0x6509B0)),
                epd.QueueAssignTo(ut.EPD(0x6509B0)),
                c.SetNextPtr(cpcache.GetVTable(), defbranch),
                block["_actions"] if "_actions" in block else [],
            ],
        )
        reset = []

        def _reset():
            nonlocal reset
            return [c.SetNextPtr(trg, nptr) for trg, nptr in reset]

        def _key_selector(keys):
            nonlocal reset
            ret = c.NextTrigger()
            if len(keys) == 1:  # Only one keys on the list
                if reset:
                    c.RawTrigger(actions=_reset())
                c.RawTrigger(
                    nextptr=cpcache.GetVTable(),
                    conditions=c.MemoryXEPD(
                        cmpplayer, c.Exactly, keys[0], bitmask
                    ),
                    actions=c.SetNextPtr(
                        cpcache.GetVTable(), casebrlist[keys[0]]
                    ),
                )

            elif len(keys) == 2:
                br1, jump1, br2 = c.Forward(), c.Forward(), c.Forward()
                br1 << c.RawTrigger(
                    nextptr=br2,
                    conditions=c.MemoryXEPD(
                        cmpplayer, c.Exactly, keys[0], bitmask
                    ),
                    actions=[c.SetNextPtr(br1, jump1), _reset()],
                )
                jump1 << c.RawTrigger(
                    nextptr=cpcache.GetVTable(),
                    actions=[
                        c.SetNextPtr(cpcache.GetVTable(), casebrlist[keys[0]]),
                        c.SetNextPtr(br1, br2),
                    ],
                )
                br2 << _key_selector(keys[1:])

            elif len(keys) >= 3:
                branch, br1, br2 = c.Forward(), c.Forward(), c.Forward()
                midpos = len(keys) // 2
                branch << c.RawTrigger(
                    nextptr=br1,
                    conditions=c.MemoryXEPD(
                        cmpplayer, c.AtLeast, keys[midpos], bitmask
                    ),
                    actions=[
                        c.SetNextPtr(branch, br2),
                        _reset(),
                    ],
                )
                br1 << _key_selector(keys[:midpos])
                reset.clear()
                reset.append((branch, br1))
                br2 << _key_selector(keys[midpos:])

            else:  # len(keys) == 0
                return defbranch

            return ret

        _key_selector(casekeylist)
    else:  # use binary search
        reset = []

        def _reset():
            nonlocal reset
            return [c.SetNextPtr(trg, nptr) for trg, nptr in reset]

        def _key_selector(keys):
            nonlocal reset
            ret = c.NextTrigger()
            if len(keys) == 1:  # Only one keys on the list
                branch, jump, goto_defbranch = (
                    c.Forward(),
                    c.Forward(),
                    c.Forward(),
                )
                branch << c.RawTrigger(
                    nextptr=goto_defbranch,
                    conditions=c.MemoryXEPD(epd, c.Exactly, keys[0], bitmask),
                    actions=[c.SetNextPtr(branch, jump), _reset()],
                )
                jump << c.RawTrigger(
                    nextptr=casebrlist[keys[0]],
                    actions=c.SetNextPtr(branch, goto_defbranch),
                )
                if reset:
                    goto_defbranch << c.RawTrigger(
                        nextptr=defbranch,
                        actions=_reset(),
                    )
                else:
                    goto_defbranch << defbranch

            elif len(keys) == 2:
                br1, jump1, br2 = c.Forward(), c.Forward(), c.Forward()
                br1 << c.RawTrigger(
                    nextptr=br2,
                    conditions=c.MemoryXEPD(epd, c.Exactly, keys[0], bitmask),
                    actions=[c.SetNextPtr(br1, jump1), _reset()],
                )
                jump1 << c.RawTrigger(
                    nextptr=casebrlist[keys[0]],
                    actions=c.SetNextPtr(br1, br2),
                )
                br2 << _key_selector(keys[1:])

            elif len(keys) >= 3:
                branch, br1, br2 = c.Forward(), c.Forward(), c.Forward()
                midpos = len(keys) // 2
                branch << c.RawTrigger(
                    nextptr=br1,
                    conditions=c.MemoryXEPD(
                        epd, c.AtLeast, keys[midpos], bitmask
                    ),
                    actions=[
                        c.SetNextPtr(branch, br2),
                        _reset(),
                    ],
                )
                br1 << _key_selector(keys[:midpos])
                reset.clear()
                reset.append((branch, br1))
                br2 << _key_selector(keys[midpos:])

            else:  # len(keys) == 0
                return defbranch

            return ret

        _key_selector(casekeylist)

    swend << c.NextTrigger()
