# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import abstractmethod
from typing import Final, Literal, Self, overload

from ... import core as c
from ... import ctrlstru as cs
from ...core import EUDVariable
from ...utils import ExprProxy, ep_assert
from .epdoffsetmap import EPDOffsetMap
from .member import BaseMember
from .memberkind import BaseKind, ByteKind, DwordKind, WordKind


class EnumMember(BaseMember, ExprProxy):
    __slots__ = (
        "_instance",
        "layout",
        "offset",
        "stride",
        "__objclass__",
        "__name__",
    )

    @property
    @abstractmethod
    def kind(self) -> type[BaseKind]:
        ...

    def __init__(
        self,
        layout: Literal["struct", "array"],
        offset: int,
        *,
        stride: int | None = None,
    ) -> None:
        self._instance: EPDOffsetMap | None = None  # FIXME
        super().__init__(layout, offset, stride=stride)
        super(BaseMember, self).__init__(None)

    def _get_epd(self, instance=None):
        if instance is None:
            instance = self._instance
        return super()._get_epd(self, instance)

    def __get__(
        self, instance: EPDOffsetMap | None, owner: type[EPDOffsetMap]
    ) -> Self:
        if instance is None:
            return self
        elif isinstance(instance, EPDOffsetMap):
            self._instance = instance
            # FIXME: fix reading value on every usages
            # example)
            # const movementFlags = unit.movementFlags;
            # arr[0] = movementFlags;
            # arr[1] = movementFlags;
            # unit.movementFlags += 1;
            # arr[2] = movementFlags;  // <- always read new value
            return self
        raise AttributeError

    def __set__(self, instance: EPDOffsetMap, value) -> None:
        self._instance = instance
        super().__set__(instance, value)

    # FIXME: Overwriting ExprProxy.getValue is kinda hacky...
    def getValue(self):  # noqa: N802
        epd, subp = self._get_epd()
        return self.kind.cast(self.kind.read_epd(epd, subp))

    def __lshift__(self, k):
        return self.getValue() << k

    def __rlshift__(self, k):
        return k << self.getValue()

    def __rshift__(self, k):
        return self.getValue() >> k

    def __rrshift__(self, k):
        return k >> self.getValue()

    def __add__(self, k):
        return self.getValue() + k

    def __radd__(self, k):
        return k + self.getValue()

    def __sub__(self, k):
        return self.getValue() - k

    def __rsub__(self, k):
        return k - self.getValue()

    def __mul__(self, k):
        return self.getValue() * k

    def __rmul__(self, k):
        return k * self.getValue()

    def __floordiv__(self, k):
        return self.getValue() // k

    def __rfloordiv__(self, k):
        return k // self.getValue()

    def __divmod__(self, k):
        return divmod(self.getValue(), k)

    def __rdivmod__(self, k):
        return divmod(k, self.getValue())

    def __mod__(self, k):
        return self.getValue() % k

    def __rmod__(self, k):
        return k % self.getValue()

    def __and__(self, k):
        return self.getValue() & k

    def __rand__(self, k):
        return k & self.getValue()

    def __or__(self, k):
        return self.getValue() | k

    def __ror__(self, k):
        return k | self.getValue()

    def __xor__(self, k):
        return self.getValue() ^ k

    def __rxor__(self, k):
        return k ^ self.getValue()

    def __neg__(self):
        return -self.getValue()

    def __invert__(self):
        return ~self.getValue()

    def __bool__(self):
        return bool(self.getValue())

    # Proxy comparison operator

    def __eq__(self, k):
        return self.getValue() == k

    def __ne__(self, k):
        return self.getValue() != k

    def __le__(self, k):
        return self.getValue() <= k

    def __lt__(self, k):
        return self.getValue() < k

    def __ge__(self, k):
        return self.getValue() >= k

    def __gt__(self, k):
        return self.getValue() > k


class ByteEnumMember(EnumMember):
    __slots__ = ()

    @property
    def kind(self):
        return ByteKind


class WordEnumMember(EnumMember):
    __slots__ = ()

    @property
    def kind(self):
        return WordKind


class DwordEnumMember(EnumMember):
    __slots__ = ()

    @property
    def kind(self):
        return DwordKind


class Flag:
    __slots__ = ("mask",)

    mask: Final[int]

    def __init__(self, mask: int) -> None:
        ep_assert(0 < mask <= 0xFFFFFFFF, f"Invalid bitmask: {mask}")
        self.mask = mask

    @overload
    def __get__(self, instance: None, owner: type[EnumMember]) -> Self:
        ...

    @overload
    def __get__(self, instance: EnumMember, owner: type[EnumMember]) -> EUDVariable:
        ...

    def __get__(self, instance, owner=None) -> EUDVariable | Self:
        if instance is None:
            return self
        if instance.layout == "struct":
            from ...trigger import Trigger

            epd, subp = instance._get_epd()
            mask = self.mask << (8 * subp)
            ret = EUDVariable()
            ret << True
            Trigger(
                c.MemoryXEPD(epd, c.AtMost, mask - 1, mask), ret.SetNumber(False)
            )
            return ret
        elif instance.layout == "array":
            # FIXME: replace to efficent implementation
            flags = instance.getValue()
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

        if instance.layout == "struct":
            epd, subp = instance._get_epd()
            mask = self.mask << (8 * subp)
            f_maskwrite_epd(epd, ~0, mask)
            if cs.EUDIfNot()(value):
                f_maskwrite_epd(epd, 0, mask)
            cs.EUDEndIf()
            return
        elif instance.layout == "array":
            # FIXME: replace to efficent implementation
            # while subp is always int for StructMember,
            # subp can be EUDVariable or int for ArrayMember
            epd, subp = instance._get_epd()
            mask = self.mask << (8 * subp)
            f_maskwrite_epd(epd, ~0, mask)
            if cs.EUDIfNot()(value):
                f_maskwrite_epd(epd, 0, mask)
            cs.EUDEndIf()
            return

        raise AttributeError


class MovementFlags(ByteEnumMember):
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
