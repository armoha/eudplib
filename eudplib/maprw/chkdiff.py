#!/usr/bin/python
# -*- coding: utf-8 -*-


import bsdiff4
from ..core.mapdata.chktok import CHK

def chkdiff(src, dst):
    """CHK Diff"""

    out = CHK()

    for sectionName in dst.enumsection():
        try:
            srcSec = src.getsection(sectionName)
        except KeyError:
            srcSec = b''
        dstSec = dst.getsection(sectionName)
        if srcSec == dstSec:
            diff = b''
        else:
            diff = bsdiff4.diff(srcSec, dstSec)

        out.setsection(sectionName, diff)

    return out.savechk()
