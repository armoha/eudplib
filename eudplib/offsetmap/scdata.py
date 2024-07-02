from ..core.rawtrigger.constenc import PlayerDict, _Player
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

# fmt: off


class TrgPlayer(_Player):
    __slots__ = ()


P1, P2, P3, P4 = TrgPlayer(0), TrgPlayer(1), TrgPlayer(2), TrgPlayer(3)
P5, P6, P7, P8 = TrgPlayer(4), TrgPlayer(5), TrgPlayer(6), TrgPlayer(7)
P9, P10, P11, P12 = TrgPlayer(8), TrgPlayer(9), TrgPlayer(10), TrgPlayer(11)
Player1, Player2, Player3, Player4 = P1, P2, P3, P4
Player5, Player6, Player7, Player8 = P5, P6, P7, P8
Player9, Player10, Player11, Player12 = P9, P10, P11, P12
CurrentPlayer = TrgPlayer(13)
Foes, Allies, NeutralPlayers = TrgPlayer(14), TrgPlayer(15), TrgPlayer(16)
AllPlayers = TrgPlayer(17)
Force1, Force2, Force3, Force4 = TrgPlayer(18), TrgPlayer(19), TrgPlayer(20), TrgPlayer(21)  # noqa: E501
NonAlliedVictoryPlayers = TrgPlayer(26)
PlayerDict.update({
    P1: 0, P2: 1, P3: 2, P4: 3,
    P5: 4, P6: 5, P7: 6, P8: 7,
    P9: 8, P10: 9, P11: 10, P12: 11,
    CurrentPlayer: 13,
    Foes: 14, Allies: 15, NeutralPlayers: 16,
    AllPlayers: 17,
    Force1: 18, Force2: 19, Force3: 20, Force4: 21,
    NonAlliedVictoryPlayers: 26,
})

# fmt: on


class TrgUnit(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeUnit(s)


class Weapon(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeWeapon(s)


class Flingy(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeFlingy(s)


class Sprite(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeSprite(s)


class Image(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeImage(s)


class Upgrade(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeUpgrade(s)


class Tech(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeTech(s)


class UnitOrder(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeUnitOrder(s)
