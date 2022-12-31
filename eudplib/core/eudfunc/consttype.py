#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from collections.abc import Callable

from ..rawtrigger import (
    EncodeAIScript,
    EncodeAllyStatus,
    EncodeComparison,
    EncodeCount,
    EncodeFlingy,
    EncodeIcon,
    EncodeImage,
    EncodeIscript,
    EncodeLocation,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodePortrait,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSprite,
    EncodeString,
    EncodeSwitch,
    EncodeSwitchAction,
    EncodeSwitchState,
    EncodeTBL,
    EncodeTech,
    EncodeUnit,
    EncodeUnitOrder,
    EncodeUpgrade,
    EncodeWeapon,
)


class createEncoder:
    @staticmethod
    def _callee(depth=2, default=None) -> str:
        import sys

        try:
            return sys._getframe(depth).f_globals["__name__"]
        except (AttributeError, ValueError):  # For platforms without _getframe()
            return default

    def __init__(self, func: Callable, name: str) -> None:
        self.__name__ = name
        self.__qualname__ = name
        self.__module__ = createEncoder._callee(default="consttype")
        self._f = func

    def cast(self, s):
        return self._f(s)

    def __repr__(self):
        return f"{self.__module__}.{self.__qualname__}"


TrgAllyStatus = createEncoder(EncodeAllyStatus, "TrgAllyStatus")
TrgComparison = createEncoder(EncodeComparison, "TrgComparison")
TrgCount = createEncoder(EncodeCount, "TrgCount")
TrgModifier = createEncoder(EncodeModifier, "TrgModifier")
TrgOrder = createEncoder(EncodeOrder, "TrgOrder")
TrgPlayer = createEncoder(EncodePlayer, "TrgPlayer")
TrgProperty = createEncoder(EncodeProperty, "TrgProperty")
TrgPropState = createEncoder(EncodePropState, "TrgPropState")
TrgResource = createEncoder(EncodeResource, "TrgResource")
TrgScore = createEncoder(EncodeScore, "TrgScore")
TrgSwitchAction = createEncoder(EncodeSwitchAction, "TrgSwitchAction")
TrgSwitchState = createEncoder(EncodeSwitchState, "TrgSwitchState")
TrgAIScript = createEncoder(EncodeAIScript, "TrgAIScript")
TrgLocation = createEncoder(EncodeLocation, "TrgLocation")
TrgString = createEncoder(EncodeString, "TrgString")
TrgSwitch = createEncoder(EncodeSwitch, "TrgSwitch")
TrgUnit = createEncoder(EncodeUnit, "TrgUnit")

StatText = createEncoder(EncodeTBL, "StatText")
Weapon = createEncoder(EncodeWeapon, "Weapon")
Flingy = createEncoder(EncodeFlingy, "Flingy")
Sprite = createEncoder(EncodeSprite, "Sprite")
Image = createEncoder(EncodeImage, "Image")
Iscript = createEncoder(EncodeIscript, "Iscript")
Upgrade = createEncoder(EncodeUpgrade, "Upgrade")
Tech = createEncoder(EncodeTech, "Tech")
UnitOrder = createEncoder(EncodeUnitOrder, "UnitOrder")
Icon = createEncoder(EncodeIcon, "Icon")
Portrait = createEncoder(EncodePortrait, "Portrait")
