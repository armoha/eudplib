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
    # grpFile = Member(0x668AA0, MemberKind.DWORD)
    isTurnable = graphicTurn = Member(0x66E860, MemberKind.BOOL)  # noqa: N815
    isClickable = Member(0x66C150, MemberKind.BOOL)  # noqa: N815
    useFullIscript = Member(0x66D4D8, MemberKind.BOOL)  # noqa: N815
    drawIfCloaked = Member(0x667718, MemberKind.BOOL)  # noqa: N815
    drawingFunction = Member(0x669E28, MemberKind.BYTE)  # noqa: N815
    # Remapping table is skipped because it doesn't work in SC:R
    # FIXME: Add UnsupportedMember
    # remapping = Member(0x669A40, MemberKind.BYTE)
    iscript = iscriptID = Member(0x66EC48, MemberKind.DWORD)  # noqa: N815
    # shieldsOverlay = Member(0x66C538, MemberKind.DWORD)
    # attackOverlay = Member(0x66B1B0, MemberKind.DWORD)
    # damageOverlay = Member(0x66A210, MemberKind.DWORD)
    # specialOverlay = Member(0x667B00, MemberKind.DWORD)
    # landingDustOverlay = Member(0x666778, MemberKind.DWORD)
    # liftOffDustOverlay = Member(0x66D8C0, MemberKind.DWORD)

    def __init__(self, index):
        super().__init__(strenc.EncodeImage(index))


ImageDataMember._data_object_type = ImageData
