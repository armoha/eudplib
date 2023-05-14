#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import binascii
import os
from collections.abc import Callable

from ..core import RegisterCreatePayloadCallback
from ..core.eudfunc.trace.tracetool import _GetTraceMap, _ResetTraceMap
from ..core.mapdata import fixmapdata, mapdata, mpqapi
from ..localize import _
from ..utils import EPError, ep_assert, ep_eprint
from .injector.apply_injector import apply_injector
from .injector.mainloop import main_starter
from .inlinecode.ilcprocesstrig import _preprocess_inline_code
from .mpqadd import _update_mpq

trace_header = None
trace_map = []


def get_trace_map() -> None:
    global trace_map, trace_header
    new_trace_header, new_trace_map = _GetTraceMap()
    if not new_trace_header[1]:
        raise EPError(_("Empty trace header"))
    if new_trace_map:
        trace_header = new_trace_header
        trace_map = list(new_trace_map)
    _ResetTraceMap()


RegisterCreatePayloadCallback(get_trace_map)


def SaveMap(fname: str, rootf: Callable, *, sector_size=None) -> None:  # noqa: N802
    """Save output map with root function.

    :param fname: Path for output map.
    :param rootf: Main entry function.
    """
    from ctypes import GetLastError

    print(_("Saving to {}...").format(fname))
    chkt = mapdata.GetChkTokenized()

    _ResetTraceMap()

    # Add payload
    root = main_starter(rootf)
    _preprocess_inline_code(chkt)
    mapdata.UpdateMapData()

    fixmapdata.FixMapData(chkt)
    apply_injector(chkt, root)

    chkt.optimize()
    rawchk = chkt.savechk()
    print(f"Output scenario.chk : {len(rawchk) / 1000000:.3}MB")
    mw = mpqapi.MPQ()

    if sector_size and isinstance(sector_size, int):
        if os.path.isfile(fname):
            e = _("You lacks permission to get access rights for output map")
            try:
                os.remove(fname)
            except PermissionError:
                ep_eprint(
                    e,
                    _("Try to turn off antivirus or StarCraft"),
                    sep="\n",
                )
                raise
        if not mw.Create(fname, sector_size=sector_size):
            raise EPError(
                _("Fail to access output map ({})").format(GetLastError())
            )
        for n, f in mapdata.IterListFiles():
            if f:
                ep_assert(
                    mw.PutFile(n, f),
                    _("Fail to export input map data to output map"),
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
            raise EPError(
                _("Fail to access output map ({})").format(GetLastError())
            )

    if not mw.PutFile("staredit\\scenario.chk", rawchk):
        raise EPError(_("Fail to add scenario.chk"))
    _update_mpq(mw)
    ep_assert(mw.Compact(), _("Fail to compact MPQ"))
    mw.Close()

    if trace_map:
        trace_fname = fname + ".epmap"
        print(_("Writing trace file to {}").format(trace_fname))
        if trace_header is None:
            raise EPError(_("Unreachable callback error"))
        with open(trace_fname, "w", encoding="utf-8") as wf:
            wf.write(
                "H0: %s\n" % binascii.hexlify(trace_header[0]).decode("ascii")
            )
            wf.write(
                "H1: %s\n" % binascii.hexlify(trace_header[1]).decode("ascii")
            )
            for k, v in trace_map:
                wf.write(f" - {k:08}%08X : {v}\n")
