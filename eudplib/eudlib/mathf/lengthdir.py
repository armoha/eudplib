#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import math

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..memiof import f_dwread_epd


@c.EUDFunc
def f_lengthdir(length, angle):
    # sin, cos table
    clist = []
    slist = []

    for i in range(91):
        cosv = math.floor(math.cos(math.pi / 180 * i) * 65536 + 0.5)
        sinv = math.floor(math.sin(math.pi / 180 * i) * 65536 + 0.5)
        clist.append(ut.i2b4(cosv))
        slist.append(ut.i2b4(sinv))

    cdb = c.Db(b"".join(clist))
    sdb = c.Db(b"".join(slist))

    # MAIN LOGIC

    if cs.EUDIf()(angle >= 360):
        angle %= 360
    cs.EUDEndIf()

    # sign of cos, sin
    sign = c.EUDLightVariable()
    tableangle = c.EUDVariable()

    # get cos, sin from table
    if cs.EUDIf()(angle <= 89):
        c.VProc(angle, [sign.SetNumber(0), angle.QueueAssignTo(tableangle)])

    if cs.EUDElseIf()(angle <= 179):
        c.VProc(
            angle,
            [
                sign.SetNumber(1),
                tableangle.SetNumber(180),
                angle.QueueSubtractTo(tableangle),
            ],
        )

    if cs.EUDElseIf()(angle <= 269):
        c.VProc(
            angle,
            [
                sign.SetNumber(3),
                angle.QueueAddTo(tableangle),
                tableangle.SetNumber(-180),
            ],
        )

    if cs.EUDElse()():
        c.VProc(
            angle,
            [
                sign.SetNumber(2),
                angle.QueueSubtractTo(tableangle),
                tableangle.SetNumber(360),
            ],
        )

    cs.EUDEndIf()

    tablecos = f_dwread_epd(ut.EPD(cdb) + tableangle)
    tableangle += ut.EPD(sdb)
    tablesin = f_dwread_epd(tableangle)

    # calculate lengthdir: cos, sin * 65536
    ldir_x = tablecos
    ldir_x *= length
    ldir_x //= 65536

    ldir_y = tablesin
    ldir_y *= length
    ldir_y //= 65536

    # restore sign of cos, sin
    c.RawTrigger(
        conditions=sign.ExactlyX(1, 1),
        actions=[  # ldir_x = -ldir_x
            ldir_x.AddNumberX(0xFFFFFFFF, 0x55555555),
            ldir_x.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            ldir_x.AddNumber(1),
        ],
    )

    c.RawTrigger(
        conditions=sign.ExactlyX(2, 2),
        actions=[  # ldir_y = -ldir_y
            ldir_y.AddNumberX(0xFFFFFFFF, 0x55555555),
            ldir_y.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            ldir_y.AddNumber(1),
        ],
    )

    return ldir_x, ldir_y


@c.EUDFunc
def f_lengthdir_256(length, angle):
    # sin, cos table
    clist = []
    slist = []

    for i in range(65):
        cosv = math.floor(math.cos(math.pi / 128 * i) * 65536 + 0.5)
        sinv = math.floor(math.sin(math.pi / 128 * i) * 65536 + 0.5)
        clist.append(ut.i2b4(cosv))
        slist.append(ut.i2b4(sinv))

    cdb = c.Db(b"".join(clist))
    sdb = c.Db(b"".join(slist))

    # MAIN LOGIC
    cs.DoActions(angle.AddNumber(192), angle.SetNumberX(0, ~255))

    # sign of cos, sin
    sign = c.EUDLightVariable()
    tableangle = c.EUDVariable()

    # get cos, sin from table
    if cs.EUDIf()(angle <= 63):
        c.VProc(angle, [sign.SetNumber(0), angle.QueueAssignTo(tableangle)])

    if cs.EUDElseIf()(angle <= 127):
        c.VProc(
            angle,
            [
                sign.SetNumber(1),
                tableangle.SetNumber(128),
                angle.QueueSubtractTo(tableangle),
            ],
        )

    if cs.EUDElseIf()(angle <= 191):
        c.VProc(
            angle,
            [
                sign.SetNumber(3),
                angle.QueueAddTo(tableangle),
                tableangle.SetNumber(-128),
            ],
        )

    if cs.EUDElse()():
        c.VProc(
            angle,
            [
                sign.SetNumber(2),
                angle.QueueSubtractTo(tableangle),
                tableangle.SetNumber(256),
            ],
        )

    cs.EUDEndIf()

    tablecos = f_dwread_epd(ut.EPD(cdb) + tableangle)
    tableangle += ut.EPD(sdb)
    tablesin = f_dwread_epd(tableangle)

    # calculate lengthdir: cos, sin * 65536
    ldir_x = tablecos
    ldir_x *= length
    ldir_x //= 65536

    ldir_y = tablesin
    ldir_y *= length
    ldir_y //= 65536

    # restore sign of cos, sin
    c.RawTrigger(
        conditions=sign.ExactlyX(1, 1),
        actions=[  # ldir_x = -ldir_x
            ldir_x.AddNumberX(0xFFFFFFFF, 0x55555555),
            ldir_x.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            ldir_x.AddNumber(1),
        ],
    )

    c.RawTrigger(
        conditions=sign.ExactlyX(2, 2),
        actions=[  # ldir_y = -ldir_y
            ldir_y.AddNumberX(0xFFFFFFFF, 0x55555555),
            ldir_y.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            ldir_y.AddNumber(1),
        ],
    )

    return ldir_x, ldir_y
