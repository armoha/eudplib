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


from ..localize import _
from .eperror import EPError

g_encoding: str = "cp949"


def UbconvSetEncoding(encoding: str) -> None:
    global g_encoding
    g_encoding = encoding


def u2b(s: str | bytes) -> bytes:
    if isinstance(s, str):
        try:
            return s.encode(g_encoding)
        except UnicodeEncodeError:
            return s.encode("utf-8")
    elif isinstance(s, bytes):
        return s
    else:
        raise EPError(_("Invalid type {}").format(type(s)))


def b2u(b: str | bytes) -> str:
    if isinstance(b, bytes):
        return b.decode(g_encoding)
    elif isinstance(b, str):
        return b
    else:
        raise EPError(_("Invalid type {}").format(type(b)))


def u2utf8(s: str | bytes) -> bytes:
    if isinstance(s, str):
        return s.encode("utf-8")
    elif isinstance(s, bytes):
        return s
    else:
        raise EPError(_("Invalid type {}").format(type(s)))
