#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import MemberKind, SCDataObjectMember
from .scdataobject import SCDataObject


class UnitData(SCDataObject):
    maxHP = hitPoints = SCDataObjectMember(0x662350, MemberKind.DWORD)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeUnit(index))
