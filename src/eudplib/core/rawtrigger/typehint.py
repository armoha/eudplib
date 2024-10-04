from typing import TYPE_CHECKING, TypeAlias

from ...utils import ExprProxy
from .constenc import (
    TrgAllyStatus,
    TrgComparison,
    TrgCount,
    TrgModifier,
    TrgOrder,
    # TrgProperty
    TrgPropState,
    TrgResource,
    TrgScore,
    TrgSwitchAction,
    TrgSwitchState,
    UnitProperty,
    _Player,
)
from .consttype import Byte, Dword, Word
from .strdict import (
    DefaultAIScriptAtLocation,
    DefaultAIScriptWithoutLocation,
    DefaultFlingy,
    DefaultIcon,
    DefaultImage,
    DefaultIscript,
    DefaultPortrait,
    DefaultRank,
    DefaultSfxData,
    DefaultSprite,
    DefaultStatText,
    DefaultTech,
    DefaultUnit,
    DefaultUnitOrder,
    DefaultUpgrade,
    DefaultWeapon,
)

if TYPE_CHECKING:
    from ...scdata import Flingy as _Flingy
    from ...scdata import Image as _Image
    from ...scdata import Sprite as _Sprite
    from ...scdata import Tech as _Tech
    from ...scdata import TrgUnit
    from ...scdata import UnitOrder as _UnitOrder
    from ...scdata import Upgrade as _Upgrade
    from ...scdata import Weapon as _Weapon

AllyStatus: TypeAlias = "TrgAllyStatus | Byte | ExprProxy[AllyStatus]"
Comparison: TypeAlias = "TrgComparison | Byte | ExprProxy[Comparison]"
Count: TypeAlias = "TrgCount | Byte | ExprProxy[Count]"
Modifier: TypeAlias = "TrgModifier | Byte | ExprProxy[Modifier]"
Order: TypeAlias = "TrgOrder | Byte | ExprProxy[Order]"
PropState: TypeAlias = "TrgPropState | Byte | ExprProxy[PropState]"
Resource: TypeAlias = "TrgResource | Byte | ExprProxy[Resource]"
Score: TypeAlias = "TrgScore | Byte | ExprProxy[Score]"
SwitchAction: TypeAlias = "TrgSwitchAction | Byte | ExprProxy[SwitchAction]"
SwitchState: TypeAlias = "TrgSwitchState | Byte | ExprProxy[SwitchState]"
TrgProperty: TypeAlias = "UnitProperty | bytes | ExprProxy[TrgProperty]"

AIScriptAtLocation: TypeAlias = (
    DefaultAIScriptAtLocation | str | bytes | Dword | ExprProxy["AIScriptAtLocation"]
)
"""4-characters AIScript are also allowed for input"""
AIScriptWithoutLocation: TypeAlias = """(
    DefaultAIScriptWithoutLocation
    | str
    | bytes
    | Dword
    | ExprProxy[AIScriptWithoutLocation]
)"""
Icon: TypeAlias = "DefaultIcon | Word | ExprProxy[Icon]"
Iscript: TypeAlias = "DefaultIscript | Dword | ExprProxy[Iscript]"
Portrait: TypeAlias = "DefaultPortrait | Word | ExprProxy[Portrait]"
Rank: TypeAlias = "DefaultRank | Byte | ExprProxy[Rank]"
SfxData: TypeAlias = "DefaultSfxData | str | Word | ExprProxy[SfxData]"
"""sfxdata.dat entries are case-insensitive"""
StatText: TypeAlias = "DefaultStatText | str | Word | ExprProxy[StatText]"

Flingy: TypeAlias = "DefaultFlingy | _Flingy | Byte | ExprProxy[Flingy]"
Image: TypeAlias = "DefaultImage | _Image | Word | ExprProxy[Image]"
Player: TypeAlias = "_Player | Dword | ExprProxy[Player]"
Sprite: TypeAlias = "DefaultSprite | _Sprite | Word | ExprProxy[Sprite]"
Tech: TypeAlias = "DefaultTech | _Tech | Byte | ExprProxy[Tech]"
Unit: TypeAlias = "DefaultUnit | TrgUnit | Word | ExprProxy[Unit]"
UnitOrder: TypeAlias = "DefaultUnitOrder | _UnitOrder | Byte | ExprProxy[UnitOrder]"
Upgrade: TypeAlias = "DefaultUpgrade | _Upgrade | Byte | ExprProxy[Upgrade]"
Weapon: TypeAlias = "DefaultWeapon | _Weapon | Byte | ExprProxy[Weapon]"

Location: TypeAlias = "str | Dword | bytes | ExprProxy[Location]"
String: TypeAlias = "str | Word | bytes | ExprProxy[String]"
Switch: TypeAlias = "str | Byte | bytes | ExprProxy[Switch]"
"""Byte in Condition, Dword in Action"""
