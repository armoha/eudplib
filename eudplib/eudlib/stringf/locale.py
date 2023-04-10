from ...core import (
    AllPlayers,
    Db,
    EUDFunc,
    EUDReturn,
    EUDVariable,
    Exactly,
    Memory,
    RawTrigger,
    SetMemory,
    SetTo,
)
from ...ctrlstru import EUDEndSwitch, EUDSwitch, EUDSwitchCase, EUDSwitchDefault
from ...utils import EPD, ExprProxy, ep_assert
from .cpprint import f_raise_CCMU

LOCALES = (
    "enUS",  # [1] English
    "frFR",  # [2] Français
    "itIT",  # [3] Italiano
    "deDE",  # [4] Deutsch
    "esES",  # [5] Español - España
    "esMX",  # [6] Español - Latino
    "ptBR",  # [7] Português
    "zhCN",  # [8] 简体中文
    "zhTW",  # [9] 繁體中文
    "jaJP",  # [10] 日本語
    "koUS",  # [11] 한국어 (음역)
    "koKR",  # [12] 한국어 (완역)
    "plPL",  # [13] Polski
    "ruRU",  # [14] Русский
)


class LocalLocale(ExprProxy):
    def __init__(self, initvar) -> None:
        self.dontFlatten = True
        super().__init__(initvar)

    def __lshift__(self, other):
        if isinstance(other, str):
            ep_assert(other in LOCALES)
            other = 1 + LOCALES.index(other)
        return super().__lshift__(other)

    def __eq__(self, other):
        if isinstance(other, str):
            ep_assert(other in LOCALES)
            other = 1 + LOCALES.index(other)
        return super().__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            ep_assert(other in LOCALES)
            other = 1 + LOCALES.index(other)
        return super().__ne__(other)

    @staticmethod
    @EUDFunc
    def _fmt(locale):
        EUDSwitch(locale)
        for i, _locale in enumerate(LOCALES):
            if EUDSwitchCase()(i + 1):
                EUDReturn(EPD(Db(_locale)))
        if EUDSwitchDefault()():
            EUDReturn(EPD(Db("(unknown locale)")))
        EUDEndSwitch()

    def fmt(self):
        from .eudprint import epd2s

        return epd2s(LocalLocale._fmt(self))


LocalLocale = LocalLocale(EUDVariable(0))


def _detect_locale():
    MAGIC_NUMBERS = {
        "enUS": (1650552405, 1948280172, 1919098991),
        "frFR": (1869638985, 1651078003, 1679844716),
        "itIT": (1869638985, 1651078003, 543517801),
        "deDE": (543516996, 1752066373, 544500069),
        "esES": (1931505486, 1634213989, 1685024800),
        "esMX": (1931505486, 1970282597, 543515749),
        "ptBR": (1869638985, 2915267443, 543974774),
        "zhCN": (3869284326, 2296747443, 3132876187),
        "zhTW": (3869344999, 3152385459, 2692803002),
        "jaJP": (3819340771, 2212727683, 2290344835),
        "koUS": (3953171692, 2649529227, 2213290116),
        "koKR": (3953171692, 2649529227, 2213290116),
        "plPL": (543517006, 3167055725, 1931501934),
        "ruRU": (3050347984, 3498299680, 3501248692),
    }

    f_raise_CCMU(AllPlayers)
    STATUS_MSG = 0x640B60 + 218 * 12
    for locale_id, locale in enumerate(LOCALES):
        magic_numbers = MAGIC_NUMBERS[locale]
        # FIXME: Can't disambiguate between koUS and koKR
        if locale == "koKR":
            continue
        RawTrigger(
            conditions=[
                Memory(STATUS_MSG, Exactly, magic_numbers[0]),
                Memory(STATUS_MSG + 4, Exactly, magic_numbers[1]),
                Memory(STATUS_MSG + 8, Exactly, magic_numbers[2]),
            ],
            actions=LocalLocale.SetNumber(locale_id + 1),
        )
    # clear error message
    RawTrigger(actions=SetMemory(STATUS_MSG, SetTo, 0))
