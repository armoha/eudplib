## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH
# (Line 1) var x = 1 << 4;
x = _IGVA(1, lambda: [_LSH(1,4)])
# (Line 2) EUDOnStart(function () { x += x; });
@EUDFunc
def _lambda1():
    x.__iadd__(x)

EUDOnStart(_lambda1)
# (Line 3) function test_compatibility() {
@EUDFunc
def f_test_compatibility():
    # (Line 4) static var ret = 0;
    ret = EUDVariable(0)
    # (Line 5) const empty = Db(i2b4(0));
    empty = Db(i2b4(0))
    # (Line 6) const cond = Forward();
    cond = Forward()
    # (Line 8) py_exec("from helper import *\n\
    # (Line 15) ");
    exec("from helper import *\nwith expect_eperror():\n    Trigger(cond, ret.AddNumber(1 << 0))\nwith expect_eperror():\n    Trigger(empty, ret.AddNumber(1 << 1))\nwith expect_eperror():\n    Trigger(empty + 1, ret.AddNumber(1 << 2))\n")
    # (Line 17) cond.__lshift__(Memory(empty, AtLeast, 1));
    cond.__lshift__(Memory(empty, AtLeast, 1))
    # (Line 18) if (cond) { ret += 1 << 3; }
    if EUDIf()(cond):
        ret.__iadd__(_LSH(1,3))
        # (Line 19) ret += x;
    EUDEndIf()
    ret.__iadd__(x)
    # (Line 20) return ret;
    EUDReturn(ret)
    # (Line 21) }