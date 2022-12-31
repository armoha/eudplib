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

import os
from typing import TypeVar

from ..core.mapdata import chktok, mapdata, mpqapi
from ..localize import _
from ..utils import ep_assert, ep_eprint
from .mpqadd import UpdateFileListByListfile

AnyPath = TypeVar("AnyPath", str, bytes, os.PathLike[str], os.PathLike[bytes])


def LoadMap(fname: AnyPath) -> None:
    """Load basemap from fname

    :param fname: Path for basemap.
    """

    print(_("Loading map {}").format(fname))
    if not os.path.isfile(fname):
        raise FileNotFoundError(_("input path is not a map file"))
    try:
        rawfile = open(fname, "rb").read()
    except FileNotFoundError:
        ep_eprint(_("input map does not exist"))
        raise
    except PermissionError:
        ep_eprint(
            _("You lacks permission to get access rights for input map"),
            _("Try to turn off antivirus or StarCraft"),
            sep="\n",
        )
        raise
    mpqr = mpqapi.MPQ()
    ep_assert(mpqr.Open(fname), _("Fail to open input map"))
    chkt = chktok.CHK()
    b = mpqr.Extract("staredit\\scenario.chk")
    ep_assert(b, _("Fail to extract scenario.chk, maybe invalid scx"))
    chkt.loadchk(b)
    mapdata.InitMapData(chkt, rawfile)
    UpdateFileListByListfile(mpqr)
    for f in mpqr.EnumFiles():
        if f and not f in ("staredit\\scenario.chk", "(listfile)"):
            mapdata.AddListFiles(f, mpqr.Extract(f))
    mpqr.Close()
