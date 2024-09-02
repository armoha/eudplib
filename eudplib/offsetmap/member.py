#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta, abstractmethod
from typing import Final, NoReturn

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from .memberkind import BaseKind, MemberKind


class BaseMember(metaclass=ABCMeta):
    """Base descriptor class for EPDOffsetMap"""

    __slots__ = ()

    offset: Final[int]
    kind: Final[type[BaseKind]]

    def __init__(self, offset: int, kind: MemberKind) -> None:
        self.offset = offset  # type: ignore[misc]
        self.kind = kind.impl()  # type: ignore[misc]
        ut.ep_assert(offset % 4 + self.kind.size() <= 4, _("Malaligned member"))

    @abstractmethod
    def __get__(self, instance, owner=None):
        ...

    @abstractmethod
    def __set__(self, instance, value) -> None:
        ...


class StructMember(BaseMember):
    __slots__ = ("offset", "kind")

    def __init__(self, offset: int, kind: MemberKind) -> None:
        super().__init__(offset, kind)

    def _get_epd(self, instance):
        q, r = divmod(self.offset, 4)
        return instance._epd + q, r

    def __get__(self, instance, owner=None) -> "c.EUDVariable | StructMember":
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            epd, subp = self._get_epd(instance)
            return self.kind.cast(self.kind.read_epd(epd, subp))
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        if isinstance(instance, EPDOffsetMap):
            epd, subp = self._get_epd(instance)
            self.kind.write_epd(epd, subp, self.kind.cast(value))
            return
        raise AttributeError


class ArrayMember(BaseMember):
    __slots__ = ("offset", "kind", "stride")

    def __init__(
        self, offset: int, kind: MemberKind, *, stride: int | None = None
    ) -> None:
        ut.ep_assert(offset % 4 == 0)
        super().__init__(offset, kind)
        if stride is None:
            self.stride = self.kind.size()
        else:
            ut.ep_assert(self.kind.size() <= stride and stride in (1, 2, 4))
            self.stride = stride

    def _get_epd(self, instance):
        # TODO: lazy calculate division
        if self.stride == 1:
            q, r = c.f_div(instance, 4)
        elif self.stride == 2:
            q, r = c.f_div(instance, 2)
            if c.IsEUDVariable(r):
                c.RawTrigger(conditions=r.Exactly(1), actions=r.SetNumber(2))
            elif r == 1:
                r = 2
        else:
            q, r = instance, 0
        return ut.EPD(self.offset) + q, r

    def __get__(self, instance, owner=None) -> "c.EUDVariable | ArrayMember":
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            epd, subp = self._get_epd(instance)
            return self.kind.cast(self.kind.read_epd(epd, subp))
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        if isinstance(instance, EPDOffsetMap):
            epd, subp = self._get_epd(instance)
            self.kind.write_epd(epd, subp, self.kind.cast(value))
            return
        raise AttributeError


class UnsupportedMember(BaseMember):
    """Not supported EUD"""

    __slots__ = ("offset", "kind", "name")

    def __set_name__(self, owner, name) -> None:
        self.name = name

    def __get__(self, instance, owner=None) -> "UnsupportedMember":
        if instance is None:
            return self
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))

    def __set__(self, instance, value) -> NoReturn:
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))


class StructEnumMember(BaseMember, ut.ExprProxy):
    __slots__ = ("offset", "kind", "_epd")

    def __init__(self, offset: int, kind: MemberKind) -> None:
        self._epd: int | c.EUDVariable = 0  # FIXME
        super().__init__(offset, kind)
        super(BaseMember, self).__init__(None)

    def _get_epd(self, instance=None):
        q, r = divmod(self.offset, 4)
        if instance is None:
            return self._epd + q, r
        return instance._epd + q, r

    # FIXME: Overwriting ExprProxy.getValue is kinda hacky...
    def getValue(self):  # noqa: N802
        epd, subp = self._get_epd()
        return self.kind.cast(self.kind.read_epd(epd, subp))

    def __get__(self, instance, owner=None) -> "StructEnumMember":
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            self._epd = instance._epd
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
            self._epd = instance._epd
            epd, subp = self._get_epd(instance)
            self.kind.write_epd(epd, subp, self.kind.cast(value))
            return
        raise AttributeError


class ArrayEnumMember(BaseMember, ut.ExprProxy):
    __slots__ = ("offset", "kind", "stride", "_instance")

    def __init__(
        self, offset: int, kind: MemberKind, *, stride: int | None = None
    ) -> None:
        ut.ep_assert(offset % 4 == 0)
        self._instance: int | c.EUDVariable = 0  # FIXME
        super().__init__(offset, kind)
        super(BaseMember, self).__init__(None)
        if stride is None:
            self.stride = self.kind.size()
        else:
            ut.ep_assert(self.kind.size() <= stride and stride in (1, 2, 4))
            self.stride = stride

    def _get_epd(self, instance=None):
        # TODO: lazy calculate division
        if instance is None:
            instance = self._instance
        if self.stride == 1:
            q, r = c.f_div(instance, 4)
        elif self.stride == 2:
            q, r = c.f_div(instance, 2)  # TODO: new function for subp 0, 2
            if c.IsEUDVariable(r):
                c.RawTrigger(conditions=r.Exactly(1), actions=r.SetNumber(2))
            elif r == 1:
                r = 2
        else:
            q, r = instance, 0
        return ut.EPD(self.offset) + q, r

    # FIXME: Overwriting ExprProxy.getValue is kinda hacky...
    def getValue(self):  # noqa: N802
        epd, subp = self._get_epd()
        return self.kind.cast(self.kind.read_epd(epd, subp))

    def __get__(self, instance, owner=None) -> "ArrayEnumMember":
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
        ut.ep_assert(mask != 0)
        self.mask = mask

    def __get__(self, instance, owner=None) -> c.EUDVariable:
        if instance is None:
            return self
        if isinstance(instance, StructEnumMember):
            from ..trigger import Trigger

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
                conditions=flags.AtMost(mask - 1, mask), actions=ret.SetNumber(False)
            )
            return ret

        raise AttributeError

    def __set__(self, instance, value) -> None:
        from ..memio import f_maskwrite_epd

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
