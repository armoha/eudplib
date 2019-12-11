import gettext
import locale
import os
import sys
from typing import Type
from types import TracebackType

_lc = os.environ.get("LANG")
if _lc is None:
    _lc, _e = locale.getdefaultlocale()

_h = sys.excepthook
_u = sys.unraisablehook
_locale_path = os.path.dirname(__file__)
_t = gettext.translation("eudplib", _locale_path, languages=[_lc], fallback=True)
if not isinstance(_t, gettext.GNUTranslations):
    _locale_path = os.path.dirname(os.path.dirname(os.path.dirname(_locale_path)))
    _t = gettext.translation("eudplib", _locale_path, languages=[_lc], fallback=True)
_, _t = _t.gettext, _t.gettext


def _excepthook(
    type_: Type[BaseException], value: BaseException, traceback: TracebackType
) -> None:
    # print("# FIXME: excepthook")
    v = list(value.args)
    for i, s in enumerate(v):
        v[i] = _t(s)
    value.args = tuple(v)
    _h(type_, value, traceback)


def _unraisablehook(unraisable):
    # print("# FIXME: unraisablehook")
    err_msg = unraisable.err_msg
    obj = unraisable.object
    if err_msg is None:
        err_msg = "Exception ignored in"
    err_msg = _t(err_msg)
    print(f"{err_msg}: {obj!r}")


sys.excepthook = _excepthook
sys.unraisablehook = _unraisablehook
