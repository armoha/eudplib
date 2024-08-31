#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal

from .. import core as c

# from .. import utils as ut
from .memberkind import BaseKind


class ByteKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[1]:
        return 1

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_bread_epd

        return f_bread_epd(epd, subp)

    @classmethod
    def write_epd(cls, epd, subp, value) -> None:
        from ..memio import f_bwrite_epd

        f_bwrite_epd(epd, subp, value)

    @classmethod
    def add_epd(cls, epd, subp, value) -> None:
        from ..memio import f_badd_epd

        f_badd_epd(epd, subp, value)

    @classmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        from ..memio import f_bsubtract_epd

        f_bsubtract_epd(epd, subp, value)


class BoolKind(ByteKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio.specialized import _boolread_epd

        return _boolread_epd()[subp](epd)


class PlayerKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import TrgPlayer

        return TrgPlayer.cast(other)

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio.specialized import _playerread_epd

        return _playerread_epd()[subp](epd)


class WeaponKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Weapon

        return Weapon.cast(other)


class UnitOrderKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import UnitOrder

        return UnitOrder.cast(other)


class UpgradeKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Upgrade

        return Upgrade.cast(other)


class TechKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Tech

        return Tech.cast(other)


class WordKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[2]:
        return 2

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_wread_epd

        return f_wread_epd(epd, subp)

    @classmethod
    def write_epd(cls, epd, subp, value) -> None:
        from ..memio import f_wwrite_epd

        f_wwrite_epd(epd, subp, value)

    @classmethod
    def add_epd(cls, epd, subp, value) -> None:
        from ..memio import f_wadd_epd

        f_wadd_epd(epd, subp, value)

    @classmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        from ..memio import f_wsubtract_epd

        f_wsubtract_epd(epd, subp, value)


class PositionXKind(WordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio.specialized import _mapxread_epd

        return _mapxread_epd()[subp // 2](epd)


class PositionYKind(WordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio.specialized import _mapyread_epd

        return _mapyread_epd()[subp // 2](epd)


class UnitKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import TrgUnit

        return TrgUnit.cast(other)

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_bread_epd

        return f_bread_epd(epd, subp)


class FlingyKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Flingy

        return Flingy.cast(other)

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_bread_epd

        return f_bread_epd(epd, subp)


class SpriteKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Sprite

        return Sprite.cast(other)


class ImageKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Image

        return Image.cast(other)


class DwordKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[4]:
        return 4

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_dwread_epd

        return f_dwread_epd(epd)

    @classmethod
    def write_epd(cls, epd, subp, value) -> None:
        from ..memio import f_dwwrite_epd

        f_dwwrite_epd(epd, value)

    @classmethod
    def add_epd(cls, epd, subp, value) -> None:
        from ..memio import f_dwadd_epd

        f_dwadd_epd(epd, value)

    @classmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        from ..memio import f_dwsubtract_epd

        f_dwsubtract_epd(epd, value)


class PositionKind(DwordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_maskread_epd
        from ..memio.specialized import _map_xy_mask

        return f_maskread_epd(epd, (lambda x, y: x + 65536 * y)(*_map_xy_mask()))


class CUnitKind(DwordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from .cunit import CUnit

        return CUnit.from_read(epd)


class CSpriteKind(DwordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> c.EUDVariable:
        from ..memio import f_spriteepdread_epd

        return f_spriteepdread_epd(epd)


class SelfKind(BaseKind):
    __slots__ = ()
