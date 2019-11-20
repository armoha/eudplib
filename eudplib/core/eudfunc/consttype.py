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

from ..rawtrigger import (
    EncodeAllyStatus,
    EncodeComparison,
    EncodeCount,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSwitchAction,
    EncodeSwitchState,
    EncodeAIScript,
    EncodeLocation,
    EncodeLocationIndex,
    EncodeUnit,
    EncodeString,
    EncodeSwitch,
    EncodeTBL,
)


def createEncoder(f):
    class _:
        @staticmethod
        def cast(s):
            return f(s)

    return _


TrgAllyStatus = createEncoder(EncodeAllyStatus)
TrgComparison = createEncoder(EncodeComparison)
TrgCount = createEncoder(EncodeCount)
TrgModifier = createEncoder(EncodeModifier)
TrgOrder = createEncoder(EncodeOrder)
TrgPlayer = createEncoder(EncodePlayer)
TrgProperty = createEncoder(EncodeProperty)
TrgPropState = createEncoder(EncodePropState)
TrgResource = createEncoder(EncodeResource)
TrgScore = createEncoder(EncodeScore)
TrgSwitchAction = createEncoder(EncodeSwitchAction)
TrgSwitchState = createEncoder(EncodeSwitchState)
TrgAIScript = createEncoder(EncodeAIScript)
TrgLocation = createEncoder(EncodeLocation)
TrgLocationIndex = createEncoder(EncodeLocationIndex)
TrgString = createEncoder(EncodeString)
TrgSwitch = createEncoder(EncodeSwitch)
TrgUnit = createEncoder(EncodeUnit)
TrgTBL = createEncoder(EncodeTBL)
