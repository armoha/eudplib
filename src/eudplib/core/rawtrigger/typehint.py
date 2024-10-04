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
    DefaultButtonSet,
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
    from ...scdata import (
        Flingy,
        Image,
        Sprite,
        Tech,
        TrgUnit,
        UnitOrder,
        Upgrade,
        Weapon,
    )

AllyStatus: TypeAlias = "TrgAllyStatus | Byte | ExprProxy[AllyStatus]"
Comparison: TypeAlias = "TrgComparison | Byte | ExprProxy[Comparison]"
Count: TypeAlias = "TrgCount | Byte | ExprProxy[Count]"
Modifier: TypeAlias = "TrgModifier | Byte | ExprProxy[Modifier]"
_Order: TypeAlias = "TrgOrder | Byte | ExprProxy[_Order]"
PropState: TypeAlias = "TrgPropState | Byte | ExprProxy[PropState]"
Resource: TypeAlias = "TrgResource | Byte | ExprProxy[Resource]"
_Score: TypeAlias = "TrgScore | Byte | ExprProxy[_Score]"
SwitchAction: TypeAlias = "TrgSwitchAction | Byte | ExprProxy[SwitchAction]"
SwitchState: TypeAlias = "TrgSwitchState | Byte | ExprProxy[SwitchState]"
_UnitProperty: TypeAlias = "UnitProperty | bytes | ExprProxy[_UnitProperty]"

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
ButtonSet: TypeAlias = "DefaultButtonSet | Word | ExprProxy[ButtonSet]"
_Icon: TypeAlias = "DefaultIcon | Word | ExprProxy[_Icon]"
_Iscript: TypeAlias = "DefaultIscript | Dword | ExprProxy[_Iscript]"
_Portrait: TypeAlias = "DefaultPortrait | Word | ExprProxy[_Portrait]"
Rank: TypeAlias = "DefaultRank | Byte | ExprProxy[Rank]"
SfxData: TypeAlias = "DefaultSfxData | str | Word | ExprProxy[SfxData]"
"""sfxdata.dat entries are case-insensitive"""
_StatText: TypeAlias = "DefaultStatText | Word | ExprProxy[_StatText]"

_Flingy: TypeAlias = "DefaultFlingy | Flingy | Byte | ExprProxy[_Flingy]"
_Image: TypeAlias = "DefaultImage | Image | Word | ExprProxy[_Image]"
Player: TypeAlias = "_Player | Dword | ExprProxy[Player]"
_Sprite: TypeAlias = "DefaultSprite | Sprite | Word | ExprProxy[_Sprite]"
_Tech: TypeAlias = "DefaultTech | Tech | Byte | ExprProxy[_Tech]"
Unit: TypeAlias = "DefaultUnit | TrgUnit | Word | ExprProxy[Unit]"
_UnitOrder: TypeAlias = "DefaultUnitOrder | UnitOrder | Byte | ExprProxy[_UnitOrder]"
_Upgrade: TypeAlias = "DefaultUpgrade | Upgrade | Byte | ExprProxy[_Upgrade]"
_Weapon: TypeAlias = "DefaultWeapon | Weapon | Byte | ExprProxy[_Weapon]"

Location: TypeAlias = "str | Byte | bytes | ExprProxy[Location]"
String: TypeAlias = "str | Word | bytes | ExprProxy[String]"
_Switch: TypeAlias = "str | Byte | bytes | ExprProxy[_Switch]"
"""Byte in Condition, Dword in Action"""
