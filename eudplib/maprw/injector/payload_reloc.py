#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import utils as ut

from ... import core as c
from ... import ctrlstru as cs
from ... import eudlib as sf
from ...core.allocator.pbuffer import Payload

""" Stage 2 :
- Initialize payload (stage3+ + user code) & execute it
"""


def create_payload_relocator(payload: Payload) -> Payload:
    # We first build code injector.
    prtdb = c.Db(b"".join([ut.i2b4(x // 4) for x in payload.prttable]))
    ortdb = c.Db(b"".join([ut.i2b4(x // 4) for x in payload.orttable]))
    n = c.EUDVariable()

    orig_payload = c.Db(payload.data)

    if c.PushTriggerScope():
        root = c.NextTrigger()

        # Verify payload
        # Note : this is very, very basic protection method. Intended attackers
        # should be able to penetrate through this very easily

        # init prt
        if payload.prttable:
            n << len(payload.prttable)
            if cs.EUDWhile()(n >= 1):
                n += ut.EPD(prtdb) - 1
                epd, dst = sf.f_dwread_epd(n), c.Forward()
                c.VProc(
                    epd,
                    [
                        n.SubtractNumber(ut.EPD(prtdb)),
                        epd.AddNumber(ut.EPD(orig_payload)),
                        epd.SetDest(ut.EPD(dst) + 4),
                    ],
                )
                cs.DoActions(dst << c.SetDeaths(0, c.Add, orig_payload // 4, 0))
            cs.EUDEndWhile()

        # init ort
        if payload.orttable:
            n << len(payload.orttable)
            if cs.EUDWhile()(n >= 1):
                n += ut.EPD(ortdb) - 1
                epd, dst = sf.f_dwread_epd(n), c.Forward()
                c.VProc(
                    epd,
                    [
                        n.SubtractNumber(ut.EPD(ortdb)),
                        epd.AddNumber(ut.EPD(orig_payload)),
                        epd.SetDest(ut.EPD(dst) + 4),
                    ],
                )
                cs.DoActions(dst << c.SetDeaths(0, c.Add, orig_payload, 0))
            cs.EUDEndWhile()

        # Jump
        c.SetNextTrigger(orig_payload)

    c.PopTriggerScope()

    return c.CreatePayload(root)
