# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Final, Literal, Self, TypeAlias, overload

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


class BaseMember(metaclass=ABCMeta):
    """Base descriptor class/mixin for EPDOffsetMap"""

    __slots__ = ()
    layout: Final[Literal["struct", "array"]]
    offset: Final[int]
    stride: Final[int]

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        *,
        stride: int | None = None,
    ) -> None:
        self.layout = layout  # type: ignore[misc]
        self.offset = offset  # type: ignore[misc]
        size = self.kind.size()
        ut.ep_assert(offset % 4 + size <= 4, _("Malaligned member"))
        self.stride = size if stride is None else stride  # type: ignore[misc]
        ut.ep_assert(size <= self.stride, _("stride should be at least member size"))

    @property
    @abstractmethod
    def kind(self) -> type[BaseKind]:
        ...

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]):
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
        self.__objclass__ = owner  # type: ignore[misc]
        self.__name__ = name  # type: ignore[misc]
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

    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return BaseKind

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        *,
        stride: int | None = None,
    ) -> None:
        self.layout = layout  # type: ignore[misc]
        self.offset = offset  # type: ignore[misc]
        self.stride = 0 if stride is None else stride  # type: ignore[misc]

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
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return BaseKind

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        *,
        stride: int | None = None,
    ) -> None:
        self.layout = layout  # type: ignore[misc]
        self.offset = offset  # type: ignore[misc]
        self.stride = 0 if stride is None else stride  # type: ignore[misc]

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


class BoolMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return Bit0Kind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class Bit1Member(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return Bit1Kind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class ByteMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return ByteKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class PlayerMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return PlayerKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> TrgPlayer:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class WeaponMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return WeaponKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Weapon:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Weapon) -> None:
        super().__set__(instance, value)


class UnitOrderMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return UnitOrderKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> UnitOrder:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _UnitOrder) -> None:
        super().__set__(instance, value)


class UpgradeMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return UpgradeKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Upgrade:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Upgrade) -> None:
        super().__set__(instance, value)


class TechMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return TechKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Tech:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Tech) -> None:
        super().__set__(instance, value)


UnitSize: TypeAlias = Literal["Independent", "Small", "Medium", "Large"] | Byte


class UnitSizeMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return UnitSizeKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

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


class RightClickActionMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return RightClickActionKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: RightClickAction) -> None:
        super().__set__(instance, value)


MovementControl: TypeAlias = (
    Literal["FlingyDat", "PartiallyMobile_Weapon", "IscriptBin"] | Byte
)


class MovementControlMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return MovementControlKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: MovementControl) -> None:
        super().__set__(instance, value)


DamageType: TypeAlias = (
    Literal["Independent", "Explosive", "Concussive", "Normal", "IgnoreArmor"] | Byte
)


class DamageTypeMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return DamageTypeKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

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


class WeaponBehaviorMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return WeaponBehaviorKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

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


class ExplosionTypeMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return ExplosionTypeKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

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


class DrawingFunctionMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return DrawingFunctionKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

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


class AnimationMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return AnimationKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: IscriptAnimation) -> None:
        super().__set__(instance, value)


RaceResearch: TypeAlias = Literal["Zerg", "Terran", "Protoss", "All"] | Byte


class RaceResearchMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return RaceResearchKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: RaceResearch) -> None:
        super().__set__(instance, value)


WorkerCarryType: TypeAlias = (
    Literal["None", "Gas", "Ore", "GasOrOre", "PowerUp"] | Byte
)


class WorkerCarryTypeMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return WorkerCarryTypeKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: WorkerCarryType) -> None:
        super().__set__(instance, value)


class RankMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return RankKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: Rank) -> None:
        super().__set__(instance, value)


class FlingyMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return FlingyKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Flingy:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Flingy) -> None:
        super().__set__(instance, value)


class WordMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return WordKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class PositionXMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return PositionXKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class PositionYMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return PositionYKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class UnitMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return UnitKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> TrgUnit:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: Unit) -> None:
        super().__set__(instance, value)


class SpriteMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return SpriteKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Sprite:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Sprite) -> None:
        super().__set__(instance, value)


class ImageMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return ImageKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> Image:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Image) -> None:
        super().__set__(instance, value)


class StatTextMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return StatTextKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _StatText) -> None:
        super().__set__(instance, value)


class SfxDataMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return SfxDataKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: SfxData) -> None:
        super().__set__(instance, value)


class PortraitMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return PortraitKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Portrait) -> None:
        super().__set__(instance, value)


class IconMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return IconKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Icon) -> None:
        super().__set__(instance, value)


class MapStringMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return MapStringKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: String) -> None:
        super().__set__(instance, value)


class ButtonSetMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return ButtonSetKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: ButtonSet) -> None:
        super().__set__(instance, value)


class DwordMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return DwordKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class PositionMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return PositionKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class CUnitMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return CUnitKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> CUnit:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class CSpriteMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return CSpriteKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> CSprite:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class IscriptMember(BaseMember):
    __slots__ = ("layout", "offset", "stride", "__objclass__", "__name__")

    @property
    def kind(self):
        return IscriptKind

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self:
        ...

    @overload
    def __get__(
        self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]
    ) -> EUDVariable:
        ...

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance: EPDOffsetMap, value: _Iscript) -> None:
        super().__set__(instance, value)
