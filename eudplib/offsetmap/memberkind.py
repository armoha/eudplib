#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import enum
from abc import ABCMeta, abstractmethod
from typing import Literal


class BaseKind(metaclass=ABCMeta):
    __slots__ = ()

    @classmethod
    def cast(cls, other):
        return other

    @classmethod
    @abstractmethod
    def size(cls) -> Literal[1, 2, 4]:
        ...

    @classmethod
    @abstractmethod
    def read_epd(cls, epd, subp):
        ...

    @classmethod
    @abstractmethod
    def write_epd(cls, epd, subp, value) -> None:
        ...

    @classmethod
    @abstractmethod
    def add_epd(cls, epd, subp, value) -> None:
        ...

    @classmethod
    @abstractmethod
    def subtract_epd(cls, epd, subp, value) -> None:
        ...


class MemberKind(enum.Enum):
    __slots__ = ()
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    BIT_1 = enum.auto()
    C_UNIT = enum.auto()
    C_SPRITE = enum.auto()
    UNIT = enum.auto()
    PLAYER = enum.auto()
    UNIT_ORDER = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    WEAPON = enum.auto()
    FLINGY = enum.auto()
    SPRITE = enum.auto()
    IMAGE = enum.auto()
    ISCRIPT = enum.auto()
    UPGRADE = enum.auto()
    TECH = enum.auto()
    STATTEXT = enum.auto()
    RANK = enum.auto()
    PORTRAIT = enum.auto()
    ICON = enum.auto()
    UNIT_SIZE = enum.auto()
    RCLICK_ACTION = enum.auto()
    SFXDATA_DAT = enum.auto()
    MAP_STRING = enum.auto()
    MOVEMENT_CONTROL = enum.auto()
    DAMAGE_TYPE = enum.auto()
    WEAPON_BEHAVIOR = enum.auto()
    EXPLOSION_TYPE = enum.auto()
    DRAWING_FUNCION = enum.auto()
    ANIMATION = enum.auto()
    RACE_RESEARCH = enum.auto()
    WORKER_CARRY_TYPE = enum.auto()

    def impl(self) -> type[BaseKind]:
        from .memberimpl import (
            AnimationKind,
            Bit0Kind,
            Bit1Kind,
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

        match self:
            case MemberKind.DWORD:
                return DwordKind
            case MemberKind.WORD:
                return WordKind
            case MemberKind.BYTE:
                return ByteKind
            case MemberKind.BOOL:
                return Bit0Kind
            case MemberKind.BIT_1:
                return Bit1Kind
            case MemberKind.C_UNIT:
                return CUnitKind
            case MemberKind.C_SPRITE:
                return CSpriteKind
            case MemberKind.UNIT:
                return UnitKind
            case MemberKind.PLAYER:
                return PlayerKind
            case MemberKind.UNIT_ORDER:
                return UnitOrderKind
            case MemberKind.POSITION:
                return PositionKind
            case MemberKind.POSITION_X:
                return PositionXKind
            case MemberKind.POSITION_Y:
                return PositionYKind
            case MemberKind.WEAPON:
                return WeaponKind
            case MemberKind.FLINGY:
                return FlingyKind
            case MemberKind.SPRITE:
                return SpriteKind
            case MemberKind.IMAGE:
                return ImageKind
            case MemberKind.ISCRIPT:
                return IscriptKind
            case MemberKind.UPGRADE:
                return UpgradeKind
            case MemberKind.TECH:
                return TechKind
            case MemberKind.STATTEXT:
                return StatTextKind
            case MemberKind.RANK:
                return RankKind
            case MemberKind.PORTRAIT:
                return PortraitKind
            case MemberKind.ICON:
                return IconKind
            case MemberKind.UNIT_SIZE:
                return UnitSizeKind
            case MemberKind.RCLICK_ACTION:
                return RightClickActionKind
            case MemberKind.SFXDATA_DAT:
                return SfxDataKind
            case MemberKind.MAP_STRING:
                return MapStringKind
            case MemberKind.MOVEMENT_CONTROL:
                return MovementControlKind
            case MemberKind.DAMAGE_TYPE:
                return DamageTypeKind
            case MemberKind.WEAPON_BEHAVIOR:
                return WeaponBehaviorKind
            case MemberKind.EXPLOSION_TYPE:
                return ExplosionTypeKind
            case MemberKind.DRAWING_FUNCION:
                return DrawingFunctionKind
            case MemberKind.ANIMATION:
                return AnimationKind
            case MemberKind.RACE_RESEARCH:
                return RaceResearchKind
            case MemberKind.WORKER_CARRY_TYPE:
                return WorkerCarryTypeKind
            case _:
                raise NotImplementedError
