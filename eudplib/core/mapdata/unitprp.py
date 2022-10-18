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

from ctypes import *

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
        hitpoint=None,
        shield=None,
        energy=None,
        resource=None,
        hanger=None,
        cloaked=None,
        burrowed=None,
        intransit=None,
        hallucinated=None,
        invincible=None,
    ):
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
