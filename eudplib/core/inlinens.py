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
from typing import Any

from eudplib.utils import ep_warn

_objns: dict[str, Any] = {}


def EUDClearNamespace() -> None:
    _objns.clear()


def EUDRegisterObjectToNamespace(funcname: str, obj: Any) -> Any:
    """Register object to inline code namespace."""
    if funcname[0] != "_":
        if funcname in _objns:
            ep_warn(f"Duplicated name {funcname} for EUDRegisterObjectToNamespace")
            _objns[funcname] = None
        else:
            _objns[funcname] = obj

    return obj


def EUDRegistered(func: Callable) -> Callable:
    """Decoreator for registering class / function."""
    return EUDRegisterObjectToNamespace(func.__name__, func)


def GetEUDNamespace() -> dict[str, Any]:
    """Get list of functions that inline code can use."""
    return _objns
