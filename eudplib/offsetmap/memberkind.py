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
    ICON = enum.auto()
    W_STRING = enum.auto()

    def impl(self) -> type[BaseKind]:
        from .memberimpl import (
            Bit0Kind,
            Bit1Kind,
            ByteKind,
            CSpriteKind,
            CUnitKind,
            DwordKind,
            FlingyKind,
            IconKind,
            ImageKind,
            IscriptKind,
            PlayerKind,
            PositionKind,
            PositionXKind,
            PositionYKind,
            SpriteKind,
            StatTextKind,
            TechKind,
            UnitKind,
            UnitOrderKind,
            UpgradeKind,
            WeaponKind,
            WordKind,
            WordStringKind,
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
            case MemberKind.ICON:
                return IconKind
            case MemberKind.W_STRING:
                return WordStringKind
            case _:
                raise NotImplementedError
