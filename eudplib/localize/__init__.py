import gettext
import locale
import os
import sys
from types import TracebackType
from typing import Any

_lc = os.environ.get("LANG")
if _lc is None:
    _lc, _e = locale.getdefaultlocale()
_lang = None if _lc is None else (_lc,)

_h = sys.excepthook
_u = sys.unraisablehook
_locale_path = os.path.dirname(__file__)
_t = gettext.translation("eudplib", _locale_path, languages=_lang, fallback=True)
if not isinstance(_t, gettext.GNUTranslations):
    _locale_path = os.path.dirname(os.path.dirname(os.path.dirname(_locale_path)))
    _t = gettext.translation("eudplib", _locale_path, languages=_lang, fallback=True)
_gt = _t.gettext
_ = _gt


def _excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> Any:
    # print("# FIXME: excepthook")
    v = list(value.args)
    for i, s in enumerate(v):
        v[i] = _gt(s)
    value.args = tuple(v)
    return _h(type_, value, traceback)


def _unraisablehook(unraisable) -> None:
    # print("# FIXME: unraisablehook")
    err_msg = unraisable.err_msg
    obj = unraisable.object
    if err_msg is None:
        err_msg = "Exception ignored in"
    err_msg = _gt(err_msg)
    print(f"{err_msg}: {obj!r}")


sys.excepthook = _excepthook
sys.unraisablehook = _unraisablehook
