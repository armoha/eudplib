#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta, abstractmethod
from typing import Final, NoReturn

from .. import core as c
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

    def _get_epd(self, instance):
        raise NotImplementedError

    @abstractmethod
    def __get__(self, instance, owner=None):
        ...

    @abstractmethod
    def __set__(self, instance, value) -> None:
        ...


class StructMember(BaseMember):
    """Struct field member"""

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
    """Parallel array member"""

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
    """'Sorry, this EUD map is not supported' error is raised when it's accessed"""

    __slots__ = ("offset", "kind", "name")

    def __set_name__(self, owner, name) -> None:
        self.name = name

    def __get__(self, instance, owner=None) -> "UnsupportedMember":
        if instance is None:
            return self
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))

    def __set__(self, instance, value) -> NoReturn:
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))
