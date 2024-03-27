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
    visible = Member(0x665C48, MemberKind.BOOL)
    image = imageID = ImageDataMember(0x666160)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeSprite(index))

SpriteDataMember._data_object_type = SpriteData
