## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL
# (Line 1) function test(fn: EUDFuncPtr(0, 0)) {
@EUDTypedFunc([EUDFuncPtr(0, 0)])
def f_test(fn):
    # (Line 2) fn();
    fn()
    # (Line 3) }
    # (Line 5) EUDOnStart(function () { test(function () {}); });

@EUDFunc
def _lambda1():
    @EUDFunc
    def _lambda2():
        pass

    f_test(_lambda2)

EUDOnStart(_lambda1)
