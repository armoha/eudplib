#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ctypes import *
from struct import pack, unpack_from

from eudplib import utils as ut


class UnitProperty(LittleEndianStructure):

    """
    UnitProperty class. Used in 'Create Unit with Properties' action.
    """

    _fields_ = [
        ("sprpvalid", c_ushort),
        ("prpvalid", c_ushort),
        ("player", c_byte),
        ("hitpoint", c_byte),
        ("shield", c_byte),
        ("energy", c_byte),
        ("resource", c_uint),
        ("hanger", c_ushort),
        ("sprpflag", c_ushort),
        ("unused", c_uint),
    ]

    def __init__(
        self,
        hitpoint: int | None = None,
        shield: int | None = None,
        energy: int | None = None,
        resource: int | None = None,
        hanger: int | None = None,
        cloaked: bool | None = None,
        burrowed: bool | None = None,
        intransit: bool | None = None,
        hallucinated: bool | None = None,
        invincible: bool | None = None,
    ) -> None:
        """
        Properties : Value/None (Don't care)

        - hitpoint : 0~100(%)  if) When unit's hitpoint is greater than 167772,
        - shield   : 0~100(%)   you should give hitpoint None to make 100%% HP.
        - energy   : 0~100(%)
        - resource : 0~4294967295
        - hanger   : 0~65536 (Count)

        Special properties : True(Enabled)/False(Disabled)/None(Don't care)

        - clocked      : Unit is clocked.
        - burrowed     : Unit is burrowed.
        - intransit    : Unit is lifted. (In transit)
        - hallucinated : Unit is hallucination.
        - invincible   : Unit is invincible.

        >>> UnitProperty(hitpoint = 50, burrowed = True) # HP 50%, burrowed
        """
        ut.ep_assert(hitpoint is None or (isinstance(hitpoint, int) and 0 <= hitpoint <= 100))
        ut.ep_assert(shield is None or (isinstance(shield, int) and 0 <= shield <= 100))
        ut.ep_assert(energy is None or (isinstance(energy, int) and 0 <= energy <= 100))
        ut.ep_assert(resource is None or (isinstance(resource, int) and 0 <= resource <= 65535))
        ut.ep_assert(hanger is None or (isinstance(hanger, int) and 0 <= hanger <= 255))

        ut.ep_assert(cloaked in [None, True, False])
        ut.ep_assert(burrowed in [None, True, False])
        ut.ep_assert(intransit in [None, True, False])
        ut.ep_assert(hallucinated in [None, True, False])
        ut.ep_assert(invincible in [None, True, False])

        def prop2int(p):
            if p is None:
                return 0
            else:
                return p

        def prop2valid(p, v):
            if p is None:
                return 0
            else:
                return v

        def prop2flag(p, v):
            if p:
                return v
            else:
                return 0

        self.player = 0

        # Set properties
        self.hitpoint = prop2int(hitpoint)
        self.shield = prop2int(shield)
        self.energy = prop2int(energy)
        self.resource = prop2int(resource)
        self.hanger = prop2int(hanger)

        self.prpvalid = (
            prop2valid(hitpoint, 1 << 1)
            | prop2valid(shield, 1 << 2)
            | prop2valid(energy, 1 << 3)
            | prop2valid(resource, 1 << 4)
            | prop2valid(hanger, 1 << 5)
        )

        # Set special properties
        self.sprpvalid = (
            prop2valid(cloaked, 1 << 0)
            | prop2valid(burrowed, 1 << 1)
            | prop2valid(intransit, 1 << 2)
            | prop2valid(hallucinated, 1 << 3)
            | prop2valid(invincible, 1 << 4)
        )

        self.sprpflag = (
            prop2flag(cloaked, 1 << 0)
            | prop2flag(burrowed, 1 << 1)
            | prop2flag(intransit, 1 << 2)
            | prop2flag(hallucinated, 1 << 3)
            | prop2flag(invincible, 1 << 4)
        )


def PropertyKey(b: bytes, index: int = 0) -> bytes:
    x = list(unpack_from("<HHBBBBIHHI", b, index))

    x[0] &= 0b11111  # remove unused flags
    x[1] &= 0b111111  # remove unused flags
    x[8] &= 0b11111  # remove unused flags

    x[2] = 0  # player number, always NULL
    x[9] = 0  # padding?

    if x[3] == 100:  # 100% HP is equals to not using HP%
        x[1] &= ~0b10
    if x[4] == 100:  # 100% Shields is equals to not using Shields%
        x[1] &= ~0b100
    # Can't apply to Energy: Default energy differs between max energy (200 and 250)
    # Can't apply to Resource amount: Default amount differs between Mineral Fields and Vespene Geyser
    if x[7] == 0:  # 0 in hanger is equals to not using hanger amount
        x[1] &= ~0b100000

    if x[1] & 0b10 == 0:  # HP is not valid
        x[3] = 0
    if x[1] & 0b100 == 0:  # Shields is not valid
        x[4] = 0
    if x[1] & 0b1000 == 0:  # Energy is not valid
        x[5] = 0
    if x[1] & 0b10000 == 0:  # Resource amount is not valid
        x[6] = 0
    if x[1] & 0b100000 == 0:  # Amount in hanger is not valid
        x[7] = 0

    if x[8] & 0b1 == 0:  # No Cloak is equals to not using Cloak
        x[0] &= ~0b1
    if x[8] & 0b10 == 0:  # No Burrowed is equals to not using Burrowed
        x[0] &= ~0b10
    if x[8] & 0b100 == 0:  # No Lifted is equals to not using Lifted
        x[0] &= ~0b100
    if x[8] & 0b1000 == 0:  # No Hallucinated is equals to not using Hallucinated
        x[0] &= ~0b1000
    if x[8] & 0b10000 == 0:  # No Invincible is equals to not using Invincible
        x[0] &= ~0b10000

    if x[0] & 0b1 == 0:  # Cloak is not valid
        x[8] &= ~0b1
    if x[0] & 0b10 == 0:  # Burrowed is not valid
        x[8] &= ~0b10
    if x[0] & 0b100 == 0:  # In transit is not valid
        x[8] &= ~0b100
    if x[0] & 0b1000 == 0:  # Hallucinated is not valid
        x[8] &= ~0b1000
    if x[0] & 0b10000 == 0:  # Invincible is not valid
        x[8] &= ~0b10000

    return pack("<HHBBBBIHHI", *x)
