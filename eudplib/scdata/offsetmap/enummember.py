# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TYPE_CHECKING, Final, Self

from ... import core as c
from ... import ctrlstru as cs
from ...utils import ExprProxy, ep_assert
from .member import ArrayMember, BaseMember
from .memberkind import MemberKind

if TYPE_CHECKING:
    from .epdoffsetmap import EPDOffsetMap


class EnumMember(ExprProxy):
    __slots__ = ()

    def __init__(self):
        super().__init__(None)

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


class StructEnumMember(BaseMember, EnumMember):
    __slots__ = ("offset", "kind", "_instance", "__objclass__", "__name__")

    def __init__(self, offset: int, kind: MemberKind) -> None:
        self._instance: EPDOffsetMap | None = None  # FIXME
        super().__init__(offset, kind)
        super(BaseMember, self).__init__()

    def _get_epd(self, instance=None):
        q, r = divmod(self.offset, 4)
        if instance is None:
            instance = self._instance
        return instance._value + q, r

    def __get__(self, instance, owner=None) -> Self:
        from .epdoffsetmap import EPDOffsetMap

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

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        if isinstance(instance, EPDOffsetMap):
            self._instance = instance
            epd, subp = self._get_epd(instance)
            self.kind.write_epd(epd, subp, self.kind.cast(value))
            return
        raise AttributeError


class ArrayEnumMember(BaseMember, EnumMember):
    __slots__ = ("offset", "kind", "stride", "_instance", "__objclass__", "__name__")

    def __init__(
        self, offset: int, kind: MemberKind, *, stride: int | None = None
    ) -> None:
        self._instance: EPDOffsetMap | None = None  # FIXME
        super().__init__(offset, kind)
        super(BaseMember, self).__init__()
        if stride is None:
            self.stride: int = self.kind.size()
        else:
            ep_assert(
                self.kind.size() <= stride, "stride is greater than member size"
            )
            self.stride = stride

    def _get_epd(self, instance=None):
        if instance is None:
            instance = self._instance
        return ArrayMember._get_epd(self, instance)

    def __get__(self, instance, owner=None) -> Self:
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            self._instance = instance
            # FIXME: fix reading value on every usages
            return self
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        if isinstance(instance, EPDOffsetMap):
            self._instance = instance
            epd, subp = self._get_epd(instance)
            self.kind.write_epd(epd, subp, self.kind.cast(value))
            return
        raise AttributeError


class Flag:
    __slots__ = ("mask",)

    mask: Final[int]

    def __init__(self, mask: int) -> None:
        ep_assert(0 < mask <= 0xFFFFFFFF, f"Invalid bitmask: {mask}")
        self.mask = mask

    def __get__(self, instance, owner=None) -> c.EUDVariable | Self:
        if instance is None:
            return self
        if isinstance(instance, StructEnumMember):
            from ...trigger import Trigger

            epd, subp = instance._get_epd()
            mask = self.mask << (8 * subp)
            ret = c.EUDVariable()
            ret << True
            Trigger(
                c.MemoryXEPD(epd, c.AtMost, mask - 1, mask), ret.SetNumber(False)
            )
            return ret
        if isinstance(instance, ArrayEnumMember):
            # FIXME: replace to efficent implementation
            flags = instance.getValue()
            ret = c.EUDVariable()
            ret << True
            c.RawTrigger(
                conditions=flags.AtMostX(self.mask - 1, self.mask),
                actions=ret.SetNumber(False),
            )
            return ret

        raise AttributeError

    def __set__(self, instance, value) -> None:
        from ...memio import f_maskwrite_epd

        if isinstance(instance, StructEnumMember):
            epd, subp = instance._get_epd()
            mask = self.mask << (8 * subp)
            f_maskwrite_epd(epd, ~0, mask)
            if cs.EUDIfNot()(value):
                f_maskwrite_epd(epd, 0, mask)
            cs.EUDEndIf()
            return
        if isinstance(instance, ArrayEnumMember):
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
