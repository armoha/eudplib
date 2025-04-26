# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

from abc import abstractmethod
from typing import Final, Literal, Self, TypeVar, overload

from ... import core as c
from ... import ctrlstru as cs
from ...core import EUDVariable
from ...localize import _
from ...utils import EPError, ExprProxy, ep_assert, unProxy
from .epdoffsetmap import EPDOffsetMap
from .member import BaseMember
from .memberkind import BaseKind, ByteKind, DwordKind, WordKind


class EnumMember(ExprProxy):
    __slots__ = ("_parent", "_instance", "_is_initialized", "_value_lazy")

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return super().__getattr__(name)

    def __init__(self, parent: BaseEnum, instance: EPDOffsetMap) -> None:
        self._parent = parent
        self._instance = instance
        self._is_initialized = False
        super().__init__(None)
        self._value_lazy = c.Forward()
        c.SetNextTrigger(self._value_lazy)
        self._value_lazy << c.NextTrigger()

    @property
    def _value(self):
        if type(self._value_lazy) is c.Forward:
            c.PushTriggerScope()
            nptr = self._value_lazy.expr
            self._value_lazy.Reset()
            self._value_lazy << c.NextTrigger()

            epd, subp = self._parent._get_epd(self._instance)
            kind = self._parent.kind
            self._value_lazy = kind.cast(kind.read_epd(epd, subp))
            c.SetNextTrigger(nptr)
            c.PopTriggerScope()
        return self._value_lazy

    @_value.setter
    def _value(self, _new_value) -> None:
        if self._is_initialized is False:
            self._is_initialized = True
        else:
            raise EPError(_("EnumMember is already initialized"))


T = TypeVar("T", bound=EnumMember)


class BaseEnum(BaseMember[T]):
    __slots__ = ("_enum", "layout", "offset", "stride", "__objclass__", "__name__")

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        enum: type[T],
        *,
        stride: int | None = None,
    ) -> None:
        self._enum = enum
        super().__init__(layout, offset, stride=stride)

    @property
    @abstractmethod
    def kind(self) -> type[BaseKind]: ...

    @overload
    def __get__(self, instance: None, owner: type[EPDOffsetMap]) -> Self: ...

    @overload
    def __get__(self, instance: EPDOffsetMap, owner: type[EPDOffsetMap]) -> T: ...

    def __get__(self, instance: EPDOffsetMap | None, owner: type[EPDOffsetMap]):
        if instance is None:
            return self
        elif isinstance(instance, EPDOffsetMap):
            return self._enum(self, instance)
        raise AttributeError

    def __set__(self, instance: EPDOffsetMap, value) -> None:
        super().__set__(instance, value)


class ByteEnum(BaseEnum[T]):
    __slots__ = ()

    @property
    def kind(self):
        return ByteKind


class WordEnum(BaseEnum[T]):
    __slots__ = ()

    @property
    def kind(self):
        return WordKind


class DwordEnum(BaseEnum[T]):
    __slots__ = ()

    @property
    def kind(self):
        return DwordKind


class Flag:
    __slots__ = ("mask", "__objclass__", "__name__")

    mask: Final[int]

    def __init__(self, mask: int) -> None:
        ep_assert(0 < mask <= 0xFFFFFFFF, f"Invalid bitmask: {mask}")
        self.mask = mask

    @overload
    def __get__(self, instance: None, owner: type[EnumMember]) -> Self: ...

    @overload
    def __get__(
        self, instance: EnumMember, owner: type[EnumMember]
    ) -> EUDVariable: ...

    def __get__(self, instance: EnumMember | None, owner=None) -> EUDVariable | Self:
        if instance is None:
            return self
        parent = instance._parent
        if parent.layout == "struct":
            from ...trigger import Trigger

            epd, subp = parent._get_epd(instance._instance)
            mask = self.mask << (8 * subp)
            ret = EUDVariable()
            ret << True
            Trigger(
                c.MemoryXEPD(epd, c.AtMost, mask - 1, mask), ret.SetNumber(False)
            )
            return ret
        elif parent.layout == "array":
            # FIXME: replace to efficent implementation
            flags = instance._value
            ret = EUDVariable()
            ret << True
            c.RawTrigger(
                conditions=flags.AtMostX(self.mask - 1, self.mask),
                actions=ret.SetNumber(False),
            )
            return ret

        raise AttributeError

    def __set__(self, instance: EnumMember, value) -> None:
        from ...memio import f_maskwrite_epd

        # FIXME: replace to efficent implementation
        # while subp is always int for StructMember,
        # subp can be EUDVariable or int for ArrayMember
        parent = instance._parent
        epd, subp = parent._get_epd(instance._instance)
        mask = self.mask << (8 * subp)

        unproxied = unProxy(value)
        if isinstance(unproxied, EUDVariable):
            f_maskwrite_epd(epd, ~0, mask)
            if cs.EUDIfNot()(value):
                f_maskwrite_epd(epd, 0, mask)
            cs.EUDEndIf()
        elif unproxied in [0, False]:
            f_maskwrite_epd(epd, 0, mask)
        elif unproxied in [1, True]:
            f_maskwrite_epd(epd, ~0, mask)
        else:
            raise EPError(
                _("Can't assign {} to {}").format(
                    value, f"{self.__objclass__}.{self.__name__}"
                )
            )

    def __set_name__(self, owner: type[EnumMember], name: str) -> None:
        self.__objclass__ = owner
        self.__name__ = name


class MovementFlags(EnumMember):
    """Flags that enable/disable certain movement."""

    __slots__ = ()
    OrderedAtLeastOnce = Flag(0x01)
    Accelerating = Flag(0x02)
    Braking = Flag(0x04)
    StartingAttack = Flag(0x08)
    Moving = Flag(0x10)
    Lifted = Flag(0x20)
    BrakeOnPathStep = Flag(0x40)
    "unit decelerates when reaching the end of current path segment"
    AlwaysZero = Flag(0x80)
    HoverUnit = Flag(0xC1)
