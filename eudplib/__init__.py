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


from .localize import *

oldGlobals = set(globals().keys())

from .utils import *
from .core import *
from .trigger import *
from .ctrlstru import *
from .eudlib import *
from .epscript import *
from .trigtrg.runtrigtrg import (
    RunTrigTrigger,
    GetFirstTrigTrigger,
    GetLastTrigTrigger,
    TrigTriggerBegin,
    TrigTriggerEnd,
)

from .maprw import *


__version__ = "0.69.5"

import types

# remove modules from __all__

_alllist = []
for _k, _v in dict(globals()).items():
    if _k in oldGlobals:
        continue
    elif _k != "stocktrg" and isinstance(_v, types.ModuleType):
        continue
    elif _k[0] == "_":
        continue
    _alllist.append(_k)

__all__ = _alllist


del _k
del _v


def eudplibVersion():
    return __version__


_alllist.append("eudplibVersion")


from .epscript.epscompile import setEpsGlobals

setEpsGlobals(_alllist)
