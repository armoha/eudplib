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

from .stringmap import InitStringMap, ApplyStringMap
from .proptable import InitPropertyMap, ApplyPropertyMap
from .playerinfo import InitPlayerInfo
from .unitfix import FixUnitMap

_inited = False
_chkt = None
_origchkt = None
_rawfile = None


def InitMapData(chkt, rawfile):
    global _inited, _origchkt, _chkt, _rawfile
    _chkt = chkt
    _origchkt = chkt.clone()
    _rawfile = rawfile

    InitStringMap(chkt)
    InitPropertyMap(chkt)
    InitPlayerInfo(chkt)
    FixUnitMap(chkt)
    _inited = True


def UpdateMapData():
    ApplyStringMap(_chkt)
    ApplyPropertyMap(_chkt)


def IsMapdataInitalized():
    return _inited


def GetChkTokenized():
    return _chkt


def GetOriginalChkTokenized():
    """ NEVER MODIFY ANYTHING WITHIN THIS CHKTOK """
    return _origchkt


def GetRawFile():
    return _rawfile
