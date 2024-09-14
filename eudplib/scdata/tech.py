#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeTech
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class Tech(ConstType, EPDOffsetMap):
    __slots__ = ()
    mineralCost = ArrayMember(0x656248, Mk.WORD)
    gasCost = ArrayMember(0x6561F0, Mk.WORD)
    timeCost = ArrayMember(0x6563D8, Mk.WORD)
    energyCost = ArrayMember(0x656380, Mk.WORD)
    researchRequirementOffset = ArrayMember(0x656198, Mk.WORD)
    techUseRequirementOffset = ArrayMember(0x6562F8, Mk.WORD)
    icon = ArrayMember(0x656430, Mk.ICON)
    label = ArrayMember(0x6562A0, Mk.STATTEXT)
    race = ArrayMember(0x656488, Mk.RACE_RESEARCH)
    researched = ArrayMember(0x656350, Mk.BYTE)  # UNUSED?
    broodWarFlag = ArrayMember(0x6564B4, Mk.BYTE)  # bool?

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeTech(initval))
