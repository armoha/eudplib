#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import os

from ..core.mapdata import chktok, mapdata, mpqapi
from ..localize import _
from ..utils import EPError, ep_assert, ep_eprint
from .mpqadd import UpdateFileListByListfile


def LoadMap(fname: str) -> None:
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
    if not b:
        raise EPError(_("Fail to extract scenario.chk, maybe invalid scx"))
    chkt.loadchk(b)
    mapdata.InitMapData(chkt, rawfile)
    UpdateFileListByListfile(mpqr)
    for f in mpqr.EnumFiles():
        if f and not f in ("staredit\\scenario.chk", "(listfile)"):
            mapdata.AddListFiles(f, mpqr.Extract(f))
    mpqr.Close()
