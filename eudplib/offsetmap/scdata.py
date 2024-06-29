from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import (
    EncodeFlingy,
    EncodeImage,
    EncodeSprite,
    EncodeTech,
    EncodeUnit,
    EncodeUnitOrder,
    EncodeUpgrade,
    EncodeWeapon,
)


class TrgUnit(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeUnit(s)


class Weapon(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeWeapon(s)


class Flingy(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeFlingy(s)


class Sprite(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeSprite(s)


class Image(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeImage(s)


class Upgrade(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeUpgrade(s)


class Tech(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeTech(s)


class UnitOrder(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeUnitOrder(s)
