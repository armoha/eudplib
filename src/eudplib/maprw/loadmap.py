# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os

from ..bindings._rust import mpqapi
from ..core.mapdata import chktok, mapdata
from ..localize import _
from ..utils import EPError, ep_eprint
from .mpqadd import update_filelist_by_listfile

_load_map_path = None


def LoadMap(fname: str) -> None:  # noqa: N802
    """Load basemap from fname

    :param fname: Path for basemap.
    """
    global _load_map_path

    print(_("Loading map {}").format(fname))
    if not os.path.isfile(fname):
        raise FileNotFoundError(_("input path is not a map file"))
    try:
        with open(fname, "rb") as file:
            rawfile = file.read()
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
    try:
        mpqr = mpqapi.MPQ.open(fname)
    except Exception as e:
        raise EPError(_("Fail to open input map")) from e

    try:
        b = mpqr.extract_file("staredit\\scenario.chk")
    except Exception as e:
        raise EPError(_("Fail to extract scenario.chk, maybe invalid scx")) from e
    if len(b) <= 1200:  # fake scenario.chk
        mpqr.set_file_locale(0x409)
        try:
            b = mpqr.extract_file("staredit\\scenario.chk")
        except Exception as e:
            raise EPError(
                _("Fail to extract scenario.chk, maybe invalid scx")
            ) from e
        mpqr.set_file_locale(0)
    chkt = chktok.CHK()
    chkt.loadchk(b)
    mapdata.init_map_data(chkt, rawfile)
    update_filelist_by_listfile(mpqr)
    del mpqr
    _load_map_path = fname
