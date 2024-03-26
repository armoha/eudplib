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


    def __init__(self, index):
        super().__init__(strenc.EncodeImage(index))

ImageDataMember._data_object_type = ImageData
