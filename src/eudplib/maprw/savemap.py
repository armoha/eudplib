# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import binascii
import os
import tempfile
from collections.abc import Callable

from ..bindings._rust import mpqapi
from ..core import RegisterCreatePayloadCallback
from ..core.eudfunc.trace.tracetool import _get_trace_map, _reset_trace_map
from ..core.mapdata import fixmapdata, mapdata
from ..localize import _
from ..utils import EPError
from .injector.apply_injector import apply_injector
from .injector.mainloop import main_starter
from .inlinecode.ilcprocesstrig import _preprocess_inline_code
from .mpqadd import _update_mpq

trace_header = None
trace_map = []


def get_trace_map() -> None:
    global trace_map, trace_header
    new_trace_header, new_trace_map = _get_trace_map()
    if not new_trace_header[1]:
        raise EPError(_("Empty trace header"))
    if new_trace_map:
        trace_header = new_trace_header
        trace_map = list(new_trace_map)
    _reset_trace_map()


RegisterCreatePayloadCallback(get_trace_map)


def SaveMap(fname: str, rootf: Callable, *, sector_size: int | None = None) -> None:  # noqa: N802
    """Save output map with root function.

    :param fname: Path for output map.
    :param rootf: Main entry function.
    """
    print(_("Saving to {}...").format(fname))
    chkt = mapdata.GetChkTokenized()

    _reset_trace_map()

    # Add payload
    root = main_starter(rootf)
    _preprocess_inline_code(chkt)
    mapdata.update_map_data()

    fixmapdata._fix_map_data(chkt)
    apply_injector(chkt, root)

    chkt.optimize()
    rawchk = chkt.savechk()
    print(f"\nOutput scenario.chk : {len(rawchk) / 1000000:.3f}MB")
    if sector_size is not None and isinstance(sector_size, int):
        from .loadmap import _load_map_path

        if _load_map_path is None:
            raise EPError(_("Must use LoadMap first"))

        # need to remove old file first because SFileCreateArchive2 does
        # not overwrite file and instead raise ERROR_ALREADY_EXISTS error
        if os.path.isfile(fname):
            try:
                os.remove(fname)
            except PermissionError as e:
                raise EPError(
                    _(
                        "You lack permission to access the output map"
                        "\n"
                        "Try turning off antivirus or StarCraft"
                    )
                ) from e

        try:
            mw = mpqapi.MPQ.clone_with_sector_size(
                _load_map_path, fname, sector_size
            )
        except Exception as e:
            raise EPError(_("Fail to access output map")) from e

        # add fake staredit\scenario.chk
        mw.set_file_locale(0)
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(b"")
        chk_path = f.name
        f.close()
        try:
            mw.add_file("staredit\\scenario.chk", chk_path)
        except Exception as e:
            raise EPError(_("Fail to add scenario.chk")) from e
        os.unlink(chk_path)
        mw.set_file_locale(0x409)

    else:
        # Process by modifying existing mpqfile
        try:
            with open(fname, "wb") as file:
                file.write(mapdata.GetRawFile())
        except PermissionError as e:
            raise EPError(
                _(
                    "You lack permission to access the output map"
                    "\n"
                    "Try turning off antivirus or StarCraft"
                )
            ) from e
        except Exception as e:
            raise EPError(_("Fail to access output map")) from e

        try:
            mw = mpqapi.MPQ.open(fname)
        except Exception as e:
            raise EPError(_("Fail to access output map")) from e

    # add real staredit\scenario.chk
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(bytes(rawchk))
    chk_path = f.name
    f.close()
    try:
        mw.add_file("staredit\\scenario.chk", chk_path)
    except Exception as e:
        raise EPError(_("Fail to add scenario.chk")) from e
    os.unlink(chk_path)
    mw.set_file_locale(0)

    _update_mpq(mw)
    try:
        mw.compact()
    except Exception as e:
        raise EPError(_("Fail to compact MPQ")) from e
    del mw

    if trace_map:
        trace_fname = fname + ".epmap"
        print(_("Writing trace file to {}").format(trace_fname))
        if trace_header is None:
            raise EPError(_("Unreachable callback error"))
        with open(trace_fname, "w", encoding="utf-8") as wf:
            wf.write(f"H0: {binascii.hexlify(trace_header[0]).decode('ascii')}\n")
            wf.write(f"H1: {binascii.hexlify(trace_header[1]).decode('ascii')}\n")
            for k, v in trace_map:
                wf.write(f" - {k:08X} : {v}\n")
