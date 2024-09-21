# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import gettext
import locale
import os
import sys
from types import TracebackType
from typing import Any

# Determine locale from environment or default
lc = os.environ.get("LANG")
if lc is None:
    lc, _e = locale.getdefaultlocale()

lang = None if lc is None else (lc,)

# Set up locale path and translation
locale_path = os.path.dirname(__file__)
t = gettext.translation("eudplib", locale_path, languages=lang, fallback=True)
if not isinstance(t, gettext.GNUTranslations):
    # Adjust locale_path if necessary
    locale_path = os.path.dirname(os.path.dirname(os.path.dirname(locale_path)))
    t = gettext.translation("eudplib", locale_path, languages=lang, fallback=True)

# Set up gettext function
_ = t.gettext

# Preserve original hooks
original_excepthook = sys.excepthook
original_unraisablehook = sys.unraisablehook


def excepthook(
    type_: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
) -> None:
    # Localize exception messages
    v = list(value.args)
    for i, s in enumerate(v):
        if isinstance(s, str):
            v[i] = t.gettext(s)
    value.args = tuple(v)
    original_excepthook(type_, value, traceback)


def unraisablehook(unraisable: Any) -> None:
    # Localize unraisable error messages
    err_msg = unraisable.err_msg or "Exception ignored in"
    err_msg = t.gettext(err_msg)
    obj = unraisable.object
    print(f"{err_msg}: {obj!r}")


# Set custom hooks
sys.excepthook = excepthook
sys.unraisablehook = unraisablehook

__all__ = ["_"]
