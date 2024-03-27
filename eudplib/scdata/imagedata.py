#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import ImageDataMember, Member, MemberKind
from .scdataobject import SCDataObject


class ImageData(SCDataObject):
    # Read only data skipped
    drawIfCloaked = Member(0x667718, MemberKind.BOOL)  # noqa: N815
    drawingFunction = Member(0x669E28, MemberKind.BYTE)  # noqa: N815
    # Remapping table is skipped because it doesn't work in SC:R
    clickable = Member(0x66C150, MemberKind.BOOL)
    useFullIscript = Member(0x66D4D8, MemberKind.BOOL)  # noqa: N815
    graphicsTurns = Member(0x66E860, MemberKind.BOOL)  # noqa: N815
    iscript = iscriptID = Member(0x66EC48, MemberKind.DWORD)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeImage(index))


ImageDataMember._data_object_type = ImageData
