## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL
# (Line 1) import .test_eps_misc;
# (Line 3) import py_warnings;
try:
    test_eps_misc = _RELIMP(".", "test_eps_misc")
except ImportError:
    from . import test_eps_misc
import warnings
# (Line 4) import .report.C240903;
# (Line 5) import .report.C240930;
try:
    C240903 = _RELIMP(".report", "C240903")
except ImportError:
    from .report import C240903
# (Line 6) import .report.C241219;
try:
    C240930 = _RELIMP(".report", "C240930")
except ImportError:
    from .report import C240930
# (Line 8) function square(x) : None;
try:
    C241219 = _RELIMP(".report", "C241219")
except ImportError:
    from .report import C241219
# (Line 10) const a = [
# (Line 11) square(1),
# (Line 12) square(2),
# (Line 13) square(3),
# (Line 14) square(4),
# (Line 15) square(5)
# (Line 16) ];
a = _CGFW(lambda: [_ARR(FlattenList([f_square(1), f_square(2), f_square(3), f_square(4), f_square(5)]))], 1)[0]
# (Line 18) function testLineno() {
@EUDFunc
def f_testLineno():
    # (Line 19) const foo = py_eval("warnings.warn");
    foo = eval("warnings.warn")
    # (Line 20) foo("ㅇㅅㅇ");
    foo("ㅇㅅㅇ")
    # (Line 21) }
    # (Line 23) function square(x) {

@EUDFunc
def f_square(x):
    # (Line 24) testLineno();
    f_testLineno()
    # (Line 25) return x * x; // + z.k;
    EUDReturn(x * x)
    # (Line 26) }
    # (Line 28) const receives = py_eval('[PVariable() for _ in range(8)]');

receives = _CGFW(lambda: [eval('[PVariable() for _ in range(8)]')], 1)[0]
# (Line 29) const attack_gwpID = 4;
attack_gwpID = _CGFW(lambda: [4], 1)[0]
# (Line 30) function constv_thing() {
@EUDFunc
def f_constv_thing():
    # (Line 31) foreach(i, pvar: py_enumerate(receives)) {}
    for i, pvar in enumerate(receives):
        # (Line 32) SetMemoryXEPD(EPD(0x656FB8) + attack_gwpID/4, Add, 100 << (attack_gwpID%4 * 8), 0xFF << (attack_gwpID%4 * 8));  // cooldown +100
        pass

    # (Line 33) return a[0] + a[1] + a[2] + a[3] + a[4];
    DoActions(SetMemoryXEPD(EPD(0x656FB8) + attack_gwpID // 4, Add, _LSH(100,(attack_gwpID % 4 * 8)), _LSH(0xFF,(attack_gwpID % 4 * 8))))
    EUDReturn(a[0] + a[1] + a[2] + a[3] + a[4])
    # (Line 34) }
    # (Line 36) function test_reported() {

@EUDFunc
def f_test_reported():
    # (Line 37) return C240903.updateUnitNameAndRank();
    EUDReturn(C240903.f_updateUnitNameAndRank())
    # (Line 38) }
