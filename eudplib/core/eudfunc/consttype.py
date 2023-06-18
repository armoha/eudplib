#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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
    def _callee(depth: int = 2, default=None) -> str:
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
