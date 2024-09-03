#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal

from ..core import (
    EncodeIcon,
    EncodeIscript,
    EncodePortrait,
    EncodeString,
    EncodeTBL,
    EUDVariable,
)
from ..core.rawtrigger.strdict import DefRankDict, DefSfxDataDict
from ..core.rawtrigger.strenc import _EncodeAny
from ..localize import _
from ..utils import EPError, unProxy

# from .. import utils as ut
from .memberkind import BaseKind


class ByteKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[1]:
        return 1

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
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


class Bit0Kind(ByteKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio.bwepdio import _bitread_epd

        return _bitread_epd(0x01)(epd, subp)

    @classmethod
    def write_epd(cls, epd, subp, value) -> None:
        from ..memio.bwepdio import _bitwrite_epd

        _bitwrite_epd(epd, subp, 0x01, value)

    @classmethod
    def add_epd(cls, epd, subp, value) -> None:
        raise NotImplementedError

    @classmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        raise NotImplementedError


class Bit1Kind(ByteKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio.bwepdio import _bitread_epd

        return _bitread_epd(0x02)(epd, subp)

    @classmethod
    def write_epd(cls, epd, subp, value) -> None:
        from ..memio.bwepdio import _bitwrite_epd

        _bitwrite_epd(epd, subp, 0x02, value)

    @classmethod
    def add_epd(cls, epd, subp, value) -> None:
        raise NotImplementedError

    @classmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        raise NotImplementedError


class PlayerKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import TrgPlayer

        return TrgPlayer.cast(other)

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio.specialized import _playerread_epd

        return _playerread_epd()[subp](epd)


class WeaponKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .weapon import Weapon

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


class UnitSizeKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "UnitSize",
            lambda s: {}[s],
            {
                "Independent": 0,
                "Small": 1,
                "Medium": 2,
                "Large": 3,
            },
            other,
        )


class RightClickActionKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "RightClickAction",
            lambda s: {}[s],
            {
                "NoCommand_AutoAttack": 0,
                "NormalMove_NormalAttack": 1,
                "NormalMove_NoAttack": 2,
                "NoMove_NormalAttack": 3,
                "Harvest": 4,
                "HarvestAndRepair": 5,
                "Nothing": 6,
            },
            other,
        )


class MovementControlKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "MovementControl",
            lambda s: {}[s],
            {
                "FlingyDat": 0,
                "PartiallyMobile_Weapon": 1,
                "IscriptBin": 2,
            },
            other,
        )


class DamageTypeKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "DamageType",
            lambda s: {}[s],
            {
                "Independent": 0,
                "Explosive": 1,
                "Concussive": 2,
                "Normal": 3,
                "IgnoreArmor": 4,
            },
            other,
        )


class WeaponBehaviorKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "WeaponBehavior",
            lambda s: {}[s],
            {
                "Fly_DoNotFollowTarget": 0,
                "Fly_FollowTarget": 1,
                "AppearOnTargetUnit": 2,
                "PersistOnTargetSite": 3,  # Psionic Storm
                "AppearOnTargetSite": 4,
                "AppearOnAttacker": 5,
                "AttackAndSelfDestruct": 6,
                "Bounce": 7,  # Mutalisk Glave Wurms
                "AttackNearbyArea": 8,  # Valkyrie Halo Rockets
                "GoToMaxRange": 9,  # Lurker Subterranean Spines
            },
            other,
        )


class ExplosionTypeKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "ExplosionType",
            lambda s: {}[s],
            {
                "None": 0,
                "NormalHit": 1,
                "SplashRadial": 2,
                "SplashEnemy": 3,
                "Lockdown": 4,
                "NuclearMissile": 5,
                "Parasite": 6,
                "Broodlings": 7,
                "EmpShockwave": 8,
                "Irradiate": 9,
                "Ensnare": 10,
                "Plague": 11,
                "StasisField": 12,
                "DarkSwarm": 13,
                "Consume": 14,
                "YamatoGun": 15,
                "Restoration": 16,
                "DisruptionWeb": 17,
                "CorrosiveAcid": 18,
                "MindControl": 19,
                "Feedback": 20,
                "OpticalFlare": 21,
                "Maelstrom": 22,
                "Unknown_Crash": 23,
                "SplashAir": 24,
            },
            other,
        )


class DrawingFunctionKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "DrawingFunction",
            lambda s: {}[s],
            {
                "Normal": 0,
                "NormalNoHallucination": 1,
                "NonVisionCloaking": 2,
                "NonVisionCloaked": 3,
                "NonVisionDecloaking": 4,
                "VisionCloaking": 5,
                "VisionCloaked": 6,
                "VisionDecloaking": 7,
                "EMPShockwave": 8,
                "UseRemapping": 9,
                "Shadow": 10,
                "HpBar": 11,  # crash
                "WarpTexture": 12,
                "SelectionCircle": 13,
                "PlayerColorOverride": 14,  # used for flags
                "HideGFX_ShowSizeRect": 15,
                "Hallucination": 16,
                "WarpFlash": 17,
            },
            other,
        )


class AnimationKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "IscriptAnimation",
            lambda s: {}[s],
            {
                "Init": 0,
                "Death": 1,
                "GndAttkInit": 2,
                "AirAttkInit": 3,
                "Unused1": 4,
                "GndAttkRpt": 5,
                "AirAttkRpt": 6,
                "CastSpell": 7,
                "GndAttkToIdle": 8,
                "AirAttkToIdle": 9,
                "Unused2": 10,
                "Walking": 11,
                "WalkingToIdle": 12,
                "SpecialState1": 13,
                "SpecialState2": 14,
                "AlmostBuilt": 15,
                "Built": 16,
                "Landing": 17,
                "LiftOff": 18,
                "IsWorking": 19,
                "WorkingToIdle": 20,
                "WarpIn": 21,
                "Unused3": 22,
                "StarEditInit": 23,
                "Disable": 24,
                "Burrow": 25,
                "UnBurrow": 26,
                "Enable": 27,
                "NoAnimation": 28,
            },
            other,
        )


class RaceResearchKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "race",
            lambda s: {}[s],
            {
                "Zerg": 0,
                "Terran": 1,
                "Protoss": 2,
                "All": 3,
            },
            other,
        )


class WorkerCarryTypeKind(ByteKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "CarryType",
            lambda s: {}[s],
            {
                "None": 0,
                "Gas": 1,
                "Ore": 2,
                "GasOrOre": 3,
                "PowerUp": 4,
            },
            other,
        )


class WordKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[2]:
        return 2

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
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
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio.specialized import _mapxread_epd

        return _mapxread_epd()[subp // 2](epd)


class PositionYKind(WordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio.specialized import _mapyread_epd

        return _mapyread_epd()[subp // 2](epd)


class UnitKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .unit import TrgUnit

        return TrgUnit.cast(other)

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio import f_bread_epd

        return f_bread_epd(epd, subp)


class FlingyKind(ByteKind):  # size of Flingy is byte in units.dat / word in CUnit
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        from .scdata import Flingy

        return Flingy.cast(other)


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
        from .image import Image

        return Image.cast(other)


class StatTextKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return EncodeTBL(other)


class RankKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return _EncodeAny(
            "rank",
            lambda s: {}[s],
            DefRankDict,
            other,
        )


class SfxDataKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        other = unProxy(other)
        if isinstance(other, str):
            other = other.replace("\\", "/").lower()
        return _EncodeAny(
            "sfxdata.dat",
            lambda s: {}[s],
            DefSfxDataDict,
            other,
        )


class PortraitKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return EncodePortrait(other)


class IconKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return EncodeIcon(other)


class WordStringKind(WordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        other = EncodeString(other)
        if isinstance(other, int) and not (0 <= other <= 65535):
            raise EPError(_("MapStringOldID should be 0 <= id <= 65535"))
        return other


class DwordKind(BaseKind):
    __slots__ = ()

    @classmethod
    def size(cls) -> Literal[4]:
        return 4

    @classmethod
    def read_epd(cls, epd, subp) -> EUDVariable:
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
    def read_epd(cls, epd, subp) -> EUDVariable:
        from ..memio import f_maskread_epd
        from ..memio.specialized import _map_xy_mask

        return f_maskread_epd(epd, (lambda x, y: x + 65536 * y)(*_map_xy_mask()))


class CUnitKind(DwordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp):
        from .cunit import CUnit

        return CUnit.from_read(epd)


class CSpriteKind(DwordKind):
    __slots__ = ()

    @classmethod
    def read_epd(cls, epd, subp):
        from .csprite import CSprite

        return CSprite.from_read(epd)


class IscriptKind(DwordKind):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return EncodeIscript(other)


class SelfKind(BaseKind):
    __slots__ = ()
