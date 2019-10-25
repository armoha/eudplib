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

from ... import core as c
from ... import eudlib as sf
from ... import ctrlstru as cs
from eudplib import utils as ut

""" Stage 2 :
- Initialize payload (stage3+ + user code) & execute it
"""


def CreatePayloadRelocator(payload):
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
                cs.DoActions([dst << c.SetDeaths(0, c.Add, orig_payload // 4, 0)])
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
        cs.EUDJump(orig_payload)

    c.PopTriggerScope()

    return c.CreatePayload(root)
