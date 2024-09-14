# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from ..localize import _
from .eperror import EPError

g_encoding: str = "cp949"


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


def b2utf8(b: str | bytes) -> str:
    if isinstance(b, bytes):
        return b.decode("utf-8")
    elif isinstance(b, str):
        return b
    else:
        raise EPError(_("Invalid type {}").format(type(b)))
