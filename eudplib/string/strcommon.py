# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.mapdata.stringmap import ForceAddString

_strcommon = None


def temp_string_id():
    global _strcommon
    if _strcommon is None:
        _strcommon = ForceAddString("")
    return _strcommon
