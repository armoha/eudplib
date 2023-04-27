#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eudplib.core.eudobj import EUDObject


def stack_objects(
    found_objects: "list[EUDObject]",
    dwoccupmap_dict: "dict[EUDObject, list[int]]",
    alloctable: "dict[EUDObject, int]",
) -> None:
    dwoccupmap_max_size = 0
    for obj in found_objects:
        dwoccupmap_max_size += len(dwoccupmap_dict[obj])

    # Buffer to sum all dwoccupmaps
    dwoccupmap_sum = [-1] * (dwoccupmap_max_size + 1)
    dwoccupmap = [0] * (dwoccupmap_max_size + 1)
    lallocaddr = 0
    payload_size = 0

    for obj in found_objects:
        # Convert to faster c array
        py_dwoccupmap = dwoccupmap_dict[obj]
        oclen = len(py_dwoccupmap)
        for i in range(oclen):
            dwoccupmap[i] = py_dwoccupmap[i]

        # preprocess dwoccupmap
        for i in range(oclen):
            if dwoccupmap[i] == 0:
                dwoccupmap[i] = -1
            elif i == 0 or dwoccupmap[i - 1] == -1:
                dwoccupmap[i] = i
            else:
                dwoccupmap[i] = dwoccupmap[i - 1]

        # Find appropriate position to allocate object
        i = 0
        while i < oclen:
            # Update on conflict map
            if dwoccupmap[i] != -1 and dwoccupmap_sum[lallocaddr + i] != -1:
                lallocaddr = dwoccupmap_sum[lallocaddr + i] - dwoccupmap[i]
                i = 0

            else:
                i += 1

        # Apply occupation map
        for i in range(oclen - 1, -1, -1):
            curoff = lallocaddr + i
            if dwoccupmap[i] != -1 or dwoccupmap_sum[curoff] != -1:
                if dwoccupmap_sum[curoff + 1] == -1:
                    dwoccupmap_sum[curoff] = curoff + 1
                else:
                    dwoccupmap_sum[curoff] = dwoccupmap_sum[curoff + 1]

        alloctable[obj] = lallocaddr * 4
        if (lallocaddr + oclen) * 4 > payload_size:
            payload_size = (lallocaddr + oclen) * 4
