#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import FlingyDataMember, Member, MemberKind, SpriteDataMember
from .scdataobject import SCDataObject


class FlingyData(SCDataObject):
    movementControl = Member(0x6C9858, MemberKind.BYTE)  # noqa: N815
    haltDistance = Member(0x6C9930, MemberKind.DWORD)  # noqa: N815
    acceleration = Member(0x6C9C78, MemberKind.WORD)
    turnRadius = Member(0x6C9E20, MemberKind.BYTE)  # noqa: N815
    topSpeed = Member(0x6C9EF8, MemberKind.DWORD)  # noqa: N815
    # skip unused
    sprite = spriteID = SpriteDataMember(0x6CA318)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeFlingy(index))

FlingyDataMember._data_object_type = FlingyData
