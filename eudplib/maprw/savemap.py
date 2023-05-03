#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import binascii
from collections.abc import Callable
import os

from ..core import RegisterCreatePayloadCallback
from ..core.eudfunc.trace.tracetool import _GetTraceMap, _ResetTraceMap
from ..core.mapdata import fixmapdata, mapdata, mpqapi
from ..localize import _
from ..utils import EPError, ep_assert, ep_eprint
from .injector.applyInjector import applyInjector
from .injector.mainloop import _MainStarter
from .inlinecode.ilcprocesstrig import PreprocessInlineCode
from .mpqadd import UpdateMPQ

traceHeader = None
traceMap = []


def getTraceMap() -> None:
    global traceMap, traceHeader
    newTraceHeader, newTraceMap = _GetTraceMap()
    if not newTraceHeader[1]:
        raise EPError(_("Empty trace header"))
    if newTraceMap:
        traceHeader = newTraceHeader
        traceMap = list(newTraceMap)
    _ResetTraceMap()


RegisterCreatePayloadCallback(getTraceMap)


def SaveMap(fname: str, rootf: Callable, *, sectorSize=None) -> None:
    """Save output map with root function.

    :param fname: Path for output map.
    :param rootf: Main entry function.
    """
    from ctypes import GetLastError

    print(_("Saving to {}...").format(fname))
    chkt = mapdata.GetChkTokenized()

    _ResetTraceMap()

    # Add payload
    root = _MainStarter(rootf)
    PreprocessInlineCode(chkt)
    mapdata.UpdateMapData()

    fixmapdata.FixMapData(chkt)
    applyInjector(chkt, root)

    chkt.optimize()
    rawchk = chkt.savechk()
    print("Output scenario.chk : {:.3}MB".format(len(rawchk) / 1000000))
    mw = mpqapi.MPQ()

    if sectorSize and isinstance(sectorSize, int):
        if os.path.isfile(fname):
            try:
                os.remove(fname)
            except PermissionError:
                ep_eprint(
                    _("You lacks permission to get access rights for output map"),
                    _("Try to turn off antivirus or StarCraft"),
                    sep="\n",
                )
                raise
        if not mw.Create(fname, sectorSize=sectorSize):
            raise EPError(_("Fail to access output map ({})").format(GetLastError()))
        for n, f in mapdata.IterListFiles():
            if f:
                ep_assert(
                    mw.PutFile(n, f), _("Fail to export input map data to output map")
                )
    else:
        # Process by modifying existing mpqfile
        try:
            open(fname, "wb").write(mapdata.GetRawFile())
        except PermissionError:
            ep_eprint(
                _("You lacks permission to get access rights for output map"),
                _("Try to turn off antivirus or StarCraft"),
                sep="\n",
            )
            raise
        if not mw.Open(fname):
            raise EPError(_("Fail to access output map ({})").format(GetLastError()))

    if not mw.PutFile("staredit\\scenario.chk", rawchk):
        raise EPError(_("Fail to add scenario.chk"))
    UpdateMPQ(mw)
    ep_assert(mw.Compact(), _("Fail to compact MPQ"))
    mw.Close()

    if traceMap:
        traceFname = fname + ".epmap"
        print(_("Writing trace file to {}").format(traceFname))
        if traceHeader is None:
            raise EPError(_("Unreachable callback error"))
        with open(traceFname, "w", encoding="utf-8") as wf:
            wf.write("H0: %s\n" % binascii.hexlify(traceHeader[0]).decode("ascii"))
            wf.write("H1: %s\n" % binascii.hexlify(traceHeader[1]).decode("ascii"))
            for k, v in traceMap:
                wf.write(" - %08X : %s\n" % (k, v))
