#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import ImageDataMember, Member, MemberKind, SpriteDataMember
from .scdataobject import SCDataObject


class SpriteData(SCDataObject):
    # Read only data skipped
    image = imageID = ImageDataMember(0x666160)  # noqa: N815
    # hpBarSize = Member(0x665E50, MemberKind.BYTE)
    # ??? = Member(0x666570, MemberKind.BYTE)
    isVisible = Member(0x665C48, MemberKind.BOOL)  # noqa: N815
    # selectionCircle = Member(0x665AC0, MemberKind.BYTE)
    # selectionVerticalOffset = Member(0x665FD8, MemberKind.BYTE)

    def __init__(self, index):
        super().__init__(strenc.EncodeSprite(index))


SpriteDataMember._data_object_type = SpriteData
