# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeUpgrade
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class Upgrade(ConstType, EPDOffsetMap):
    __slots__ = ()
    mineralCostBase = ArrayMember(0x655740, Mk.WORD)
    mineralCostFactor = ArrayMember(0x6559C0, Mk.WORD)
    gasCostBase = ArrayMember(0x655840, Mk.WORD)
    gasCostFactor = ArrayMember(0x6557C0, Mk.WORD)
    timeCostBase = ArrayMember(0x655B80, Mk.WORD)
    timeCostFactor = ArrayMember(0x655940, Mk.WORD)
    requirementOffset = ArrayMember(0x6558C0, Mk.WORD)
    icon = ArrayMember(0x655AC0, Mk.ICON)
    label = ArrayMember(0x655A40, Mk.STATTEXT)
    race = ArrayMember(0x655BFC, Mk.RACE_RESEARCH)
    maxLevel = ArrayMember(0x655700, Mk.BYTE)
    broodWarFlag = ArrayMember(0x655B3C, Mk.BYTE)  # bool?

    @ut.classproperty
    def range(self):
        return (0, 60, 1)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeUpgrade(initval))
