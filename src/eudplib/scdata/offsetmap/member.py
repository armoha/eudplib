# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import (
    TYPE_CHECKING,
    Final,
    Generic,
    Literal,
    Self,
    TypeAlias,
    TypeVar,
    overload,
)

from ... import core as c
from ... import utils as ut
from ...core import EUDVariable
from ...core.rawtrigger.consttype import Byte
from ...localize import _
from .epdoffsetmap import EPDOffsetMap
from .memberkind import (
    AnimationKind,
    BaseKind,
    Bit0Kind,
    Bit1Kind,
    ButtonSetKind,
    ByteKind,
    CSpriteKind,
    CUnitKind,
    DamageTypeKind,
    DrawingFunctionKind,
    DwordKind,
    ExplosionTypeKind,
    FlingyKind,
    IconKind,
    ImageKind,
    IscriptKind,
    MapStringKind,
    MovementControlKind,
    PlayerKind,
    PortraitKind,
    PositionKind,
    PositionXKind,
    PositionYKind,
    RaceResearchKind,
    RankKind,
    RightClickActionKind,
    SfxDataKind,
    SpriteKind,
    StatTextKind,
    TechKind,
    UnitKind,
    UnitOrderKind,
    UnitSizeKind,
    UpgradeKind,
    WeaponBehaviorKind,
    WeaponKind,
    WordKind,
    WorkerCarryTypeKind,
    _NeverKind,
)

if TYPE_CHECKING:
    from ...core.rawtrigger.typehint import (
        ButtonSet,
        Rank,
        SfxData,
        String,
        Unit,
        _Flingy,
        _Icon,
        _Image,
        _Iscript,
        _Portrait,
        _Sprite,
        _StatText,
        _Tech,
        _UnitOrder,
        _Upgrade,
        _Weapon,
    )
    from ..csprite import CSprite
    from ..cunit import CUnit
    from ..flingy import Flingy
    from ..image import Image
    from ..player import TrgPlayer
    from ..sprite import Sprite
    from ..tech import Tech
    from ..unit import TrgUnit
    from ..unitorder import UnitOrder
    from ..upgrade import Upgrade
    from ..weapon import Weapon


T = TypeVar("T")


class BaseMember(Generic[T], metaclass=ABCMeta):
    """Base descriptor class/mixin for EPDOffsetMap"""

    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        *,
        stride: int | None = None,
    ) -> None:
        self.layout: Final[Literal["struct", "array"]] = layout
        self.offset: Final[int] = offset
        size = self.kind.size()
        ut.ep_assert(offset % 4 + size <= 4, _("Malaligned member"))
        self.stride: Final[int] = size if stride is None else stride
        ut.ep_assert(size <= self.stride, _("stride should be at least member size"))

    @property
    @abstractmethod
    def kind(self) -> type[BaseKind]:
        ...

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> T:
        ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        epd, subp = self._get_epd(instance)
        return self.kind.cast(self.kind.read_epd(epd, subp))

    def __set__(self, instance: EPDOffsetMap, value) -> None:
        epd, subp = self._get_epd(instance)
        self.kind.write_epd(epd, subp, self.kind.cast(value))

    def __set_name__(self, owner: type[EPDOffsetMap], name: str) -> None:
        self.__objclass__ = owner
        self.__name__ = name
        if self.layout == "array":
            owner._has_array_member = True

    def _get_epd(
        self, instance: EPDOffsetMap
    ) -> tuple[int | EUDVariable, int | EUDVariable]:
        if self.layout == "array":
            value = instance._value
            if not isinstance(value, EUDVariable):
                epd, subp = divmod(self.offset + value * self.stride, 4)
                return ut.EPD(0) + epd, subp
            if self.stride == 4:
                return ut.EPD(self.offset) + value, self.offset % 4

            # lazy calculate multiplication & division
            q, r, update = instance._get_stride_cache(self.stride)
            update_start, update_restore, update_end = update

            nexttrg = c.Forward()
            c.RawTrigger(
                nextptr=update_start,
                actions=[
                    c.SetNextPtr(update_start, update_restore),
                    c.SetMemory(update_start + 348, c.SetTo, nexttrg),
                    c.SetNextPtr(update_end, nexttrg),
                ],
            )
            nexttrg << c.NextTrigger()

            epd = ut.EPD(self.offset) + q
            if self.offset % 4 == 0:
                subp = r
            else:
                subp = self.offset % 4 + r
                if self.offset % 4 + (4 - self.stride) % 4 >= 4:
                    c.RawTrigger(
                        conditions=subp.AtLeast(4),
                        actions=[subp.SubtractNumber(4), epd.AddNumber(1)],
                    )
            return epd, subp

        elif self.layout == "struct":
            quotient, remainder = divmod(self.offset, 4)
            return instance._value + quotient, remainder

        raise NotImplementedError


class UnsupportedMember(BaseMember):
    """
    'Sorry, this EUD map is not supported' error is raised when it's accessed.

    '이 EUD 지도는 스타크래프트 리마스터와 호환되지 않습니다.' 오류가 발생합니다.
    """

    __slots__ = ()

    @property
    def kind(self):
        return _NeverKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]):
        ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raise ut.EPError(
            _(
                "StarCraft: Remastered does not support {} "
                "and causes in-game errors."
            ).format(f"{self.__objclass__}.{self.__name__}")
        )

    def __set__(self, instance: EPDOffsetMap, value) -> None:
        raise ut.EPError(
            _(
                "StarCraft: Remastered does not support {} "
                "and causes in-game errors."
            ).format(f"{self.__objclass__}.{self.__name__}")
        )


class NotImplementedMember(BaseMember):
    __slots__ = ()

    @property
    def kind(self):
        return _NeverKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]):
        ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raise ut.EPError(
            _("{} is not implemented for {}").format(
                self.__name__, self.__objclass__
            )
        )

    def __set__(self, instance: EPDOffsetMap, value) -> None:
        raise ut.EPError(
            _("{} is not implemented for {}").format(
                self.__name__, self.__objclass__
            )
        )


class BoolMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return Bit0Kind


class Bit1Member(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return Bit1Kind


class ByteMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return ByteKind


class PlayerMember(BaseMember["TrgPlayer"]):
    __slots__ = ()

    @property
    def kind(self):
        return PlayerKind


class WeaponMember(BaseMember["Weapon"]):
    __slots__ = ()

    @property
    def kind(self):
        return WeaponKind

    def __set__(self, instance: EPDOffsetMap, value: _Weapon) -> None:
        super().__set__(instance, value)


class UnitOrderMember(BaseMember["UnitOrder"]):
    __slots__ = ()

    @property
    def kind(self):
        return UnitOrderKind

    def __set__(self, instance: EPDOffsetMap, value: _UnitOrder) -> None:
        super().__set__(instance, value)


class UpgradeMember(BaseMember["Upgrade"]):
    __slots__ = ()

    @property
    def kind(self):
        return UpgradeKind

    def __set__(self, instance: EPDOffsetMap, value: _Upgrade) -> None:
        super().__set__(instance, value)


class TechMember(BaseMember["Tech"]):
    __slots__ = ()

    @property
    def kind(self):
        return TechKind

    def __set__(self, instance: EPDOffsetMap, value: _Tech) -> None:
        super().__set__(instance, value)


UnitSize: TypeAlias = Literal["Independent", "Small", "Medium", "Large"] | Byte


class UnitSizeMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return UnitSizeKind

    def __set__(self, instance: EPDOffsetMap, value: UnitSize) -> None:
        super().__set__(instance, value)


RightClickAction: TypeAlias = (
    Literal[
        "NoCommand_AutoAttack",
        "NormalMove_NormalAttack",
        "NormalMove_NoAttack",
        "NoMove_NormalAttack",
        "Harvest",
        "HarvestAndRepair",
        "Nothing",
    ]
    | Byte
)


class RightClickActionMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return RightClickActionKind

    def __set__(self, instance: EPDOffsetMap, value: RightClickAction) -> None:
        super().__set__(instance, value)


MovementControl: TypeAlias = (
    Literal["FlingyDat", "PartiallyMobile_Weapon", "IscriptBin"] | Byte
)


class MovementControlMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return MovementControlKind

    def __set__(self, instance: EPDOffsetMap, value: MovementControl) -> None:
        super().__set__(instance, value)


DamageType: TypeAlias = (
    Literal["Independent", "Explosive", "Concussive", "Normal", "IgnoreArmor"] | Byte
)


class DamageTypeMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return DamageTypeKind

    def __set__(self, instance: EPDOffsetMap, value: DamageType) -> None:
        super().__set__(instance, value)


WeaponBehavior: TypeAlias = (
    Literal[
        "Fly_DoNotFollowTarget",
        "Fly_FollowTarget",
        "AppearOnTargetUnit",
        "PersistOnTargetSite",
        "AppearOnTargetSite",
        "AppearOnAttacker",
        "AttackAndSelfDestruct",
        "Bounce",
        "AttackNearbyArea",
        "GoToMaxRange",
    ]
    | Byte
)


class WeaponBehaviorMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return WeaponBehaviorKind

    def __set__(self, instance: EPDOffsetMap, value: WeaponBehavior) -> None:
        super().__set__(instance, value)


ExplosionType: TypeAlias = (
    Literal[
        "None",
        "NormalHit",
        "SplashRadial",
        "SplashEnemy",
        "Lockdown",
        "NuclearMissile",
        "Parasite",
        "Broodlings",
        "EmpShockwave",
        "Irradiate",
        "Ensnare",
        "Plague",
        "StasisField",
        "DarkSwarm",
        "Consume",
        "YamatoGun",
        "Restoration",
        "DisruptionWeb",
        "CorrosiveAcid",
        "MindControl",
        "Feedback",
        "OpticalFlare",
        "Maelstrom",
        "Unknown_Crash",
        "SplashAir",
    ]
    | Byte
)


class ExplosionTypeMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return ExplosionTypeKind

    def __set__(self, instance: EPDOffsetMap, value: ExplosionType) -> None:
        super().__set__(instance, value)


DrawingFunction: TypeAlias = (
    Literal[
        "Normal",
        "NormalNoHallucination",
        "NonVisionCloaking",
        "NonVisionCloaked",
        "NonVisionDecloaking",
        "VisionCloaking",
        "VisionCloaked",
        "VisionDecloaking",
        "EMPShockwave",
        "UseRemapping",
        "Shadow",
        "HpBar",
        "WarpTexture",
        "SelectionCircle",
        "PlayerColorOverride",
        "HideGFX_ShowSizeRect",
        "Hallucination",
        "WarpFlash",
    ]
    | Byte
)


class DrawingFunctionMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return DrawingFunctionKind

    def __set__(self, instance: EPDOffsetMap, value: DrawingFunction) -> None:
        super().__set__(instance, value)


IscriptAnimation: TypeAlias = (
    Literal[
        "Init",
        "Death",
        "GndAttkInit",
        "AirAttkInit",
        "Unused1",
        "GndAttkRpt",
        "AirAttkRpt",
        "CastSpell",
        "GndAttkToIdle",
        "AirAttkToIdle",
        "Unused2",
        "Walking",
        "WalkingToIdle",
        "SpecialState1",
        "SpecialState2",
        "AlmostBuilt",
        "Built",
        "Landing",
        "LiftOff",
        "IsWorking",
        "WorkingToIdle",
        "WarpIn",
        "Unused3",
        "StarEditInit",
        "Disable",
        "Burrow",
        "UnBurrow",
        "Enable",
        "NoAnimation",
    ]
    | Byte
)


class AnimationMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return AnimationKind

    def __set__(self, instance: EPDOffsetMap, value: IscriptAnimation) -> None:
        super().__set__(instance, value)


RaceResearch: TypeAlias = Literal["Zerg", "Terran", "Protoss", "All"] | Byte


class RaceResearchMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return RaceResearchKind

    def __set__(self, instance: EPDOffsetMap, value: RaceResearch) -> None:
        super().__set__(instance, value)


WorkerCarryType: TypeAlias = (
    Literal["None", "Gas", "Ore", "GasOrOre", "PowerUp"] | Byte
)


class WorkerCarryTypeMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return WorkerCarryTypeKind

    def __set__(self, instance: EPDOffsetMap, value: WorkerCarryType) -> None:
        super().__set__(instance, value)


class RankMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return RankKind

    def __set__(self, instance: EPDOffsetMap, value: Rank) -> None:
        super().__set__(instance, value)


class FlingyMember(BaseMember["Flingy"]):
    __slots__ = ()

    @property
    def kind(self):
        return FlingyKind

    def __set__(self, instance: EPDOffsetMap, value: _Flingy) -> None:
        super().__set__(instance, value)


class WordMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return WordKind


class PositionXMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return PositionXKind


class PositionYMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return PositionYKind


class UnitMember(BaseMember["TrgUnit"]):
    __slots__ = ()

    @property
    def kind(self):
        return UnitKind

    def __set__(self, instance: EPDOffsetMap, value: Unit) -> None:
        super().__set__(instance, value)


class SpriteMember(BaseMember["Sprite"]):
    __slots__ = ()

    @property
    def kind(self):
        return SpriteKind

    def __set__(self, instance: EPDOffsetMap, value: _Sprite) -> None:
        super().__set__(instance, value)


class ImageMember(BaseMember["Image"]):
    __slots__ = ()

    @property
    def kind(self):
        return ImageKind

    def __set__(self, instance: EPDOffsetMap, value: _Image) -> None:
        super().__set__(instance, value)


class StatTextMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return StatTextKind

    def __set__(self, instance: EPDOffsetMap, value: _StatText) -> None:
        super().__set__(instance, value)


class SfxDataMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return SfxDataKind

    def __set__(self, instance: EPDOffsetMap, value: SfxData) -> None:
        super().__set__(instance, value)


class PortraitMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return PortraitKind

    def __set__(self, instance: EPDOffsetMap, value: _Portrait) -> None:
        super().__set__(instance, value)


class IconMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return IconKind

    def __set__(self, instance: EPDOffsetMap, value: _Icon) -> None:
        super().__set__(instance, value)


class MapStringMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return MapStringKind

    def __set__(self, instance: EPDOffsetMap, value: String) -> None:
        super().__set__(instance, value)


class ButtonSetMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return ButtonSetKind

    def __set__(self, instance: EPDOffsetMap, value: ButtonSet) -> None:
        super().__set__(instance, value)


class DwordMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return DwordKind


class PositionMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return PositionKind


class CUnitMember(BaseMember["CUnit"]):
    __slots__ = ()

    @property
    def kind(self):
        return CUnitKind


class CSpriteMember(BaseMember["CSprite"]):
    __slots__ = ()

    @property
    def kind(self):
        return CSpriteKind


class IscriptMember(BaseMember[EUDVariable]):
    __slots__ = ()

    @property
    def kind(self):
        return IscriptKind

    def __set__(self, instance: EPDOffsetMap, value: _Iscript) -> None:
        super().__set__(instance, value)
