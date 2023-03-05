#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

# Formula source : http://nghiaho.com/?p=997


@c.EUDFunc
def f_atan2(y, x):
    signflags = c.EUDVariable()
    signflags << 0

    # Check x sign
    c.RawTrigger(
        conditions=x >= 0x80000000,
        actions=[
            signflags.AddNumber(1),  # set xsign
            x.AddNumberX(0xFFFFFFFF, 0x55555555),
            x.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            x.AddNumber(1),
        ],
    )

    # Check y sign
    c.RawTrigger(
        conditions=y >= 0x80000000,
        actions=[
            signflags.AddNumber(2),  # set ysign
            y.AddNumberX(0xFFFFFFFF, 0x55555555),
            y.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            y.AddNumber(1),
        ],
    )

    # Check x/y order
    if cs.EUDIf()(y >= x):
        z = c.EUDVariable(0, c.SetTo, 0)
        # Swap x, y so that y <= x
        c.SeqCompute(
            [
                (signflags, c.Add, 4),  # set xyabscmp
                (z, c.SetTo, x),
                (x, c.SetTo, y),
                (y, None, z),
            ]
        )
    cs.EUDEndIf()

    # To prevent overflow, we limit values of y and x.
    # atan value is maximized when x = y, then atan_value = 45 * x**3
    # 45 * x**3 <= 0xFFFFFFFF : x <= 456.99....
    if cs.EUDIf()(x >= 400):
        # Normalize below 400
        divn = x // 400
        divn += 1
        x //= divn
        y //= divn
    cs.EUDEndIf()

    # Calculate arctan value
    # arctan(z) ~= z * (45 - (z-1) * (14 + 4*z)), 0 <= z <= 1
    # arctan(y/x) ~= y/x * (45 - (y-x)/x * (14x + 4y)/x))
    # arctan(y/x) ~= y * (45*x*x - (y-x)(14x+4y)) / (x*x*x)
    t1 = x * x
    t2 = y * (45 * t1 - (y - x) * (14 * x + 4 * y))
    t3 = x * t1
    atan_value = t2 // t3

    # Translate angles by sign flags
    #
    #      |  0 |  1 | xsign          |  0 |  1 | xsign
    # -----+----+----+-----      -----+----+----+-----
    #   0  |  0+|180-|             0  | 90-| 90+|
    # -----+----+----+           -----+----+----+
    #   1  |360-|180+|             1  |270+|270-|
    # -----+----+----+           -----+----+----+
    # ysign|      xyabscmp=0     ysign|      xyabscmp=1

    cs.EUDSwitch(signflags, 7)
    swblock = ut.EUDGetLastBlock()[1]
    if cs.EUDSwitchCase()(0):  # xsign, ysign, xyabscmp = 0, 0, 0
        # atan_value
        c.SetNextTrigger(swblock["swend"])
    if cs.EUDSwitchCase()(1):  # xsign, ysign, xyabscmp = 1, 0, 0
        # 180 - atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(180 + 1),
            ],
        )
    if cs.EUDSwitchCase()(2):  # xsign, ysign, xyabscmp = 0, 1, 0
        # 360 - atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(360 + 1),
            ],
        )
    if cs.EUDSwitchCase()(3):  # xsign, ysign, xyabscmp = 1, 1, 0
        # 180 + atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(180),
        )
    if cs.EUDSwitchCase()(4):  # xsign, ysign, xyabscmp = 0, 0, 1
        # 90 - atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(90 + 1),
            ],
        )
    if cs.EUDSwitchCase()(5):  # xsign, ysign, xyabscmp = 1, 0, 1
        # 90 + atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(90),
        )
    if cs.EUDSwitchCase()(6):  # xsign, ysign, xyabscmp = 0, 1, 1
        # 270 + atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(270),
        )
    if cs.EUDSwitchCase()(7):  # xsign, ysign, xyabscmp = 1, 1, 1
        # 270 - atan_value
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(270 + 1),
            ],
        )
    cs.EUDEndSwitch()
    return atan_value


@c.EUDFunc
def f_atan2_256(y, x):
    signflags = c.EUDVariable()
    signflags << 0

    # Check x sign
    c.RawTrigger(
        conditions=x >= 0x80000000,
        actions=[
            signflags.AddNumber(1),  # set xsign
            x.AddNumberX(0xFFFFFFFF, 0x55555555),
            x.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            x.AddNumber(1),
        ],
    )

    # Check y sign
    c.RawTrigger(
        conditions=y >= 0x80000000,
        actions=[
            signflags.AddNumber(2),  # set ysign
            y.AddNumberX(0xFFFFFFFF, 0x55555555),
            y.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
            y.AddNumber(1),
        ],
    )

    # Check x/y order
    if cs.EUDIf()(y >= x):
        z = c.EUDVariable(0, c.SetTo, 0)
        # Swap x, y so that y <= x
        c.SeqCompute(
            [
                (signflags, c.Add, 4),  # set xyabscmp
                (z, c.SetTo, x),
                (x, c.SetTo, y),
                (y, None, z),
            ]
        )
    cs.EUDEndIf()

    # To prevent overflow, we limit values of y and x.
    # atan value is maximized when x = y, then atan_value = 32 * 45 * x**3
    # 1440 * x**3 <= 0xFFFFFFFF : x <= 143.946....
    if cs.EUDIf()(x >= 128):
        # Normalize below 128
        divn = x // 128
        divn += 1
        x //= divn
        y //= divn
    cs.EUDEndIf()

    # Calculate arctan value
    # y * 32(45x² - (y-x)(14x+4y)) / (45x³)
    t1 = 45 * (x * x)
    t2 = y * (32 * (t1 - (y - x) * (14 * x + 4 * y)))
    t3 = x * t1
    atan_value = t2 // t3

    # Translate angles by sign flags

    cs.EUDSwitch(signflags, 7)
    swblock = ut.EUDGetLastBlock()[1]
    if cs.EUDSwitchCase()(0):  # xsign, ysign, xyabscmp = 0, 0, 0
        c.SetNextTrigger(swblock["swend"])
    if cs.EUDSwitchCase()(1):  # xsign, ysign, xyabscmp = 1, 0, 0
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(128 + 1),
            ],
        )
    if cs.EUDSwitchCase()(2):  # xsign, ysign, xyabscmp = 0, 1, 0
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(256 + 1),
            ],
        )
    if cs.EUDSwitchCase()(3):  # xsign, ysign, xyabscmp = 1, 1, 0
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(128),
        )
    if cs.EUDSwitchCase()(4):  # xsign, ysign, xyabscmp = 0, 0, 1
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(64 + 1),
            ],
        )
    if cs.EUDSwitchCase()(5):  # xsign, ysign, xyabscmp = 1, 0, 1
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(64),
        )
    if cs.EUDSwitchCase()(6):  # xsign, ysign, xyabscmp = 0, 1, 1
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=atan_value.AddNumber(192),
        )
    if cs.EUDSwitchCase()(7):  # xsign, ysign, xyabscmp = 1, 1, 1
        c.RawTrigger(
            nextptr=swblock["swend"],
            actions=[
                atan_value.AddNumberX(0xFFFFFFFF, 0x55555555),
                atan_value.AddNumberX(0xFFFFFFFF, 0xAAAAAAAA),
                atan_value.AddNumber(192 + 1),
            ],
        )
    cs.EUDEndSwitch()
    c.RawTrigger(actions=atan_value.AddNumberX(64, 255))
    return atan_value
