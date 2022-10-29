## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH
# (Line 1) import py_random;
import random
# (Line 2) import py_itertools;
import itertools
# (Line 3) import collections.deque;
from collections import deque
# (Line 4) function test_write() {
@EUDFunc
def f_test_write():
    # (Line 5) const ret = py_list();
    ret = list()
    # (Line 7) const u32 = py_eval("lambda: random.randint(1, 0xFFFFFFFF)");
    u32 = eval("lambda: random.randint(1, 0xFFFFFFFF)")
    # (Line 8) const shift = py_eval("lambda: random.randint(0, 31)");
    shift = eval("lambda: random.randint(0, 31)")
    # (Line 10) const num = u32(), u32(), u32(), u32(), u32(), u32(),
    # (Line 11) shift(), shift(), u32(), u32(), u32();
    num = u32(), u32(), u32(), u32(), u32(), u32(), shift(), shift(), u32(), u32(), u32()
    # (Line 12) const numV = EUDArray(num);
    numV = EUDArray(num)
    # (Line 13) const numS = num, numV;
    numS = num, numV
    # (Line 14) setcurpl(getuserplayerid());
    f_setcurpl(f_getuserplayerid())
    # (Line 15) const dbg = StringBuffer(3000);
    dbg = StringBuffer(3000)
    # (Line 16) dbg.insert(0);
    dbg.insert(0)
    # (Line 17) foreach(vals : numS) {
    for vals in numS:
        # (Line 18) var expect = vals[0];
        expect = _LVAR([_ARRC(vals, 0)])
        # (Line 19) expect += vals[1];
        expect.__iadd__(_ARRC(vals, 1))
        # (Line 20) expect -= vals[2];
        expect.__isub__(_ARRC(vals, 2))
        # (Line 21) dbg.appendf("\n\x07{:x}\x02 *= {:x}", expect, vals[3],);
        dbg.appendf("\n\x07{:x}\x02 *= {:x}", expect, _ARRC(vals, 3))
        # (Line 22) expect *= vals[3];
        expect.__imul__(_ARRC(vals, 3))
        # (Line 23) var temp = expect;
        temp = _LVAR([expect])
        # (Line 24) dbg.appendf(" -> \x07{:x}\x02 /= {:x}", expect, vals[4],);
        dbg.appendf(" -> \x07{:x}\x02 /= {:x}", expect, _ARRC(vals, 4))
        # (Line 25) expect /= vals[4];
        expect.__ifloordiv__(_ARRC(vals, 4))
        # (Line 26) temp += expect;
        temp.__iadd__(expect)
        # (Line 27) dbg.appendf(" -> \x07{}\x02 %= {:x}", expect, vals[5],);
        dbg.appendf(" -> \x07{}\x02 %= {:x}", expect, _ARRC(vals, 5))
        # (Line 28) expect %= vals[5];
        expect.__imod__(_ARRC(vals, 5))
        # (Line 29) temp += expect;
        temp.__iadd__(expect)
        # (Line 30) dbg.appendf(" -> \x07{}\x02 <<= {}", expect, vals[6],);
        dbg.appendf(" -> \x07{}\x02 <<= {}", expect, _ARRC(vals, 6))
        # (Line 31) expect <<= vals[6];
        expect.__ilshift__(_ARRC(vals, 6))
        # (Line 32) temp += expect;
        temp.__iadd__(expect)
        # (Line 33) dbg.appendf(" -> \x07{:x}\x02 >>= {}", expect, vals[7],);
        dbg.appendf(" -> \x07{:x}\x02 >>= {}", expect, _ARRC(vals, 7))
        # (Line 34) expect >>= vals[7];
        expect.__irshift__(_ARRC(vals, 7))
        # (Line 35) temp += expect;
        temp.__iadd__(expect)
        # (Line 38) dbg.appendf(" -> \x07{}\x02 &= {:x}", expect, vals[8]);
        dbg.appendf(" -> \x07{}\x02 &= {:x}", expect, _ARRC(vals, 8))
        # (Line 39) expect &= vals[8];
        expect.__iand__(_ARRC(vals, 8))
        # (Line 40) temp += expect;
        temp.__iadd__(expect)
        # (Line 41) dbg.appendf(" -> \x07{}\x02 |= {:x}", expect, vals[9]);
        dbg.appendf(" -> \x07{}\x02 |= {:x}", expect, _ARRC(vals, 9))
        # (Line 42) expect |= vals[9];
        expect.__ior__(_ARRC(vals, 9))
        # (Line 43) temp += expect;
        temp.__iadd__(expect)
        # (Line 44) dbg.appendf(" -> \x07{:x}", expect);
        dbg.appendf(" -> \x07{:x}", expect)
        # (Line 45) expect ^= vals[10];
        expect.__ixor__(_ARRC(vals, 10))
        # (Line 46) temp += expect;
        temp.__iadd__(expect)
        # (Line 47) ret.append(temp);
        ret.append(temp)
        # (Line 48) }
        # (Line 49) const pvar, arr = PVariable(), EUDArray(8);

    pvar, arr = List2Assignable([PVariable(), EUDArray(8)])
    # (Line 50) var v1, v2 = pvar, arr;
    v1, v2 = _LVAR([pvar, arr])
    # (Line 51) const pvarV, arrV = PVariable.cast(v1), EUDArray.cast(v2);
    pvarV, arrV = List2Assignable([PVariable.cast(v1), EUDArray.cast(v2)])
    # (Line 53) const index = py_eval("random.randint(0, 7)");
    index = eval("random.randint(0, 7)")
    # (Line 54) var indexV = index;
    indexV = _LVAR([index])
    # (Line 56) foreach(arr, i, vals : py_eval("itertools.product(\
    # (Line 58) )")) {
    for arr_1, i, vals in eval("itertools.product(        (pvar, arr, pvarV, arrV), (index, indexV), (num, numV)    )"):
        # (Line 59) arr[i] = vals[0];
        _ARRW(arr_1, i) << (_ARRC(vals, 0))
        # (Line 60) arr[i] += vals[1];
        _ARRW(arr_1, i).__iadd__(_ARRC(vals, 1))
        # (Line 61) arr[i] -= vals[2];
        _ARRW(arr_1, i).__isub__(_ARRC(vals, 2))
        # (Line 62) arr[i] *= vals[3];
        _ARRW(arr_1, i).__imul__(_ARRC(vals, 3))
        # (Line 63) var temp = arr[i];
        temp = _LVAR([_ARRC(arr_1, i)])
        # (Line 64) arr[i] /= vals[4];
        _ARRW(arr_1, i).__ifloordiv__(_ARRC(vals, 4))
        # (Line 65) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 66) arr[i] %= vals[5];
        _ARRW(arr_1, i).__imod__(_ARRC(vals, 5))
        # (Line 67) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 68) arr[i] <<= vals[6];
        _ARRW(arr_1, i).__ilshift__(_ARRC(vals, 6))
        # (Line 69) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 70) arr[i] >>= vals[7];
        _ARRW(arr_1, i).__irshift__(_ARRC(vals, 7))
        # (Line 71) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 74) arr[i] &= vals[8];
        _ARRW(arr_1, i).__iand__(_ARRC(vals, 8))
        # (Line 75) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 76) arr[i] |= vals[9];
        _ARRW(arr_1, i).__ior__(_ARRC(vals, 9))
        # (Line 77) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 78) arr[i] ^= vals[10];
        _ARRW(arr_1, i).__ixor__(_ARRC(vals, 10))
        # (Line 79) temp += arr[i];
        temp.__iadd__(_ARRC(arr_1, i))
        # (Line 80) ret.append(temp);
        ret.append(temp)
        # (Line 81) }
        # (Line 82) dbg.Display();

    dbg.Display()
    # (Line 84) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 85) }
    # (Line 86) function test_compare() {

@EUDFunc
def f_test_compare():
    # (Line 87) const ret = py_list();
    ret = list()
    # (Line 88) const num = py_eval("[random.randint(1, 0xFFFFFFFF) for _ in range(11)]");
    num = eval("[random.randint(1, 0xFFFFFFFF) for _ in range(11)]")
    # (Line 89) const numV = EUDArray(num);
    numV = EUDArray(num)
    # (Line 91) const pvar, arr = PVariable(), EUDArray(8);
    pvar, arr = List2Assignable([PVariable(), EUDArray(8)])
    # (Line 92) var v1, v2 = pvar, arr;
    v1, v2 = _LVAR([pvar, arr])
    # (Line 93) const pvarV, arrV = PVariable.cast(v1), EUDArray.cast(v2);
    pvarV, arrV = List2Assignable([PVariable.cast(v1), EUDArray.cast(v2)])
    # (Line 95) const index = py_eval("random.randint(0, 7)");
    index = eval("random.randint(0, 7)")
    # (Line 96) var indexV = index;
    indexV = _LVAR([index])
    # (Line 98) foreach(arr, i, vals : py_eval("itertools.product(\
    # (Line 100) )")) {
    for arr_1, i, vals in eval("itertools.product(        (pvar, arr, pvarV, arrV), (index, indexV), (num, numV)    )"):
        # (Line 101) var temp = 0;
        temp = _LVAR([0])
        # (Line 102) arr[i] = vals[0];
        _ARRW(arr_1, i) << (_ARRC(vals, 0))
        # (Line 103) if (arr[i] == vals[1]) temp += 1 << 1;
        if EUDIf()(_ARRC(arr_1, i) == _ARRC(vals, 1)):
            temp.__iadd__(_LSH(1,1))
            # (Line 104) if (arr[i] != vals[2]) temp += 1 << 2;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) == _ARRC(vals, 2), neg=True):
            temp.__iadd__(_LSH(1,2))
            # (Line 105) if (arr[i] >= vals[3]) temp += 1 << 3;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) >= _ARRC(vals, 3)):
            temp.__iadd__(_LSH(1,3))
            # (Line 106) if (arr[i] <= vals[4]) temp += 1 << 4;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) <= _ARRC(vals, 4)):
            temp.__iadd__(_LSH(1,4))
            # (Line 107) if (arr[i] > vals[5]) temp += 1 << 5;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) <= _ARRC(vals, 5), neg=True):
            temp.__iadd__(_LSH(1,5))
            # (Line 108) if (arr[i] < vals[6]) temp += 1 << 6;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) >= _ARRC(vals, 6), neg=True):
            temp.__iadd__(_LSH(1,6))
            # (Line 109) if (1 * arr[i] < vals[7]) temp += 1 << 7;
        EUDEndIf()
        if EUDIf()(1 * _ARRC(arr_1, i) >= _ARRC(vals, 7), neg=True):
            temp.__iadd__(_LSH(1,7))
            # (Line 110) const v8, v9 = vals[8], vals[9];
        EUDEndIf()
        v8, v9 = List2Assignable([_ARRC(vals, 8), _ARRC(vals, 9)])
        # (Line 111) if (v8 >= arr[i]) temp += 1 << 8;
        if EUDIf()(v8 >= _ARRC(arr_1, i)):
            temp.__iadd__(_LSH(1,8))
            # (Line 112) if (v9 < arr[i]) temp += 1 << 9;
        EUDEndIf()
        if EUDIf()(v9 >= _ARRC(arr_1, i), neg=True):
            temp.__iadd__(_LSH(1,9))
            # (Line 114) if (vals[10] != arr[i]) temp += 1 << 10;
        EUDEndIf()
        if EUDIf()(_ARRC(vals, 10) == _ARRC(arr_1, i), neg=True):
            temp.__iadd__(_LSH(1,10))
            # (Line 115) ret.append(temp);
        EUDEndIf()
        ret.append(temp)
        # (Line 116) }
        # (Line 118) return List2Assignable(ret);

    EUDReturn(List2Assignable(ret))
    # (Line 119) }
    # (Line 120) const q8 = EUDQueue(8)();

q8 = _CGFW(lambda: [EUDQueue(8)()], 1)[0]
# (Line 121) function test_queue() {
@EUDFunc
def f_test_queue():
    # (Line 122) var ret = 0;
    ret = _LVAR([0])
    # (Line 123) ret += q8.empty() ? 0b1 : 0;  // ret = 1
    ret.__iadd__(EUDTernary(q8.empty())(0b1)(0))
    # (Line 124) q8.append(1);
    q8.append(1)
    # (Line 125) q8.append(EUDVariable(2));
    q8.append(EUDVariable(2))
    # (Line 126) ret += 1 << q8.popleft();  // pop 1, ret = 3
    ret.__iadd__(_LSH(1,q8.popleft()))
    # (Line 127) q8.append(EUDVariable(3));
    q8.append(EUDVariable(3))
    # (Line 128) ret += q8.empty() ? 0x80000000 : 0;
    ret.__iadd__(EUDTernary(q8.empty())(0x80000000)(0))
    # (Line 129) ret += q8.popleft() == 2 ? 0b100 : 0;  // pop 2, ret = 7
    ret.__iadd__(EUDTernary(q8.popleft() == 2)(0b100)(0))
    # (Line 130) ret += q8.popleft() == 3 ? 0b1000 : 0;  // pop 3, ret = 15
    ret.__iadd__(EUDTernary(q8.popleft() == 3)(0b1000)(0))
    # (Line 131) ret += q8.empty() ? 0b10000 : 0;  // ret = 31
    ret.__iadd__(EUDTernary(q8.empty())(0b10000)(0))
    # (Line 132) return ret;
    EUDReturn(ret)
    # (Line 133) }
    # (Line 134) function test_queue_wraparound() {

@EUDFunc
def f_test_queue_wraparound():
    # (Line 135) const q3 = EUDQueue(3)();
    q3 = EUDQueue(3)()
    # (Line 136) const ret = EUDCreateVariables(6);
    ret = EUDCreateVariables(6)
    # (Line 137) var iter = 0;
    iter = _LVAR([0])
    # (Line 139) foreach(v : q3) { ret[0] += v; iter++; }
    for v in q3:
        _ARRW(ret, 0).__iadd__(v)
        iter.__iadd__(1)
        # (Line 140) q3.append(1);

    q3.append(1)
    # (Line 141) q3.append(2);
    q3.append(2)
    # (Line 143) foreach(v : q3) { ret[1] += v; iter++; }
    for v in q3:
        _ARRW(ret, 1).__iadd__(v)
        iter.__iadd__(1)
        # (Line 144) q3.append(3);

    q3.append(3)
    # (Line 145) q3.append(4);
    q3.append(4)
    # (Line 147) foreach(v : q3) { ret[2] += v; iter++; }
    for v in q3:
        _ARRW(ret, 2).__iadd__(v)
        iter.__iadd__(1)
        # (Line 149) q3.append(5);

    q3.append(5)
    # (Line 150) foreach(v : q3) { ret[3] += v; iter++; }
    for v in q3:
        _ARRW(ret, 3).__iadd__(v)
        iter.__iadd__(1)
        # (Line 152) q3.popleft();

    q3.popleft()
    # (Line 153) foreach(v : q3) { ret[4] += v; iter++; }
    for v in q3:
        _ARRW(ret, 4).__iadd__(v)
        iter.__iadd__(1)
        # (Line 155) q3.append(6);

    q3.append(6)
    # (Line 156) q3.append(7);
    q3.append(7)
    # (Line 157) foreach(v : q3) { ret[5] += v; iter++; }
    for v in q3:
        _ARRW(ret, 5).__iadd__(v)
        iter.__iadd__(1)
        # (Line 158) ret.append(iter);

    ret.append(iter)
    # (Line 159) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 160) }
    # (Line 161) const methods = py_eval('{\

# (Line 164) }');
methods = _CGFW(lambda: [eval('{    "append": "a",   "appendleft": "aL",    "pop":    "p",   "popleft":    "pL"}')], 1)[0]
# (Line 165) const DequeCases = py_eval('random.sample(sorted(methods.getValue()), 27, counts=[9, 9, 9, 9])');
DequeCases = _CGFW(lambda: [eval('random.sample(sorted(methods.getValue()), 27, counts=[9, 9, 9, 9])')], 1)[0]
# (Line 166) const DequeTest = py_eval("''.join(methods[name] for name in DequeCases)");
DequeTest = _CGFW(lambda: [eval("''.join(methods[name] for name in DequeCases)")], 1)[0]
# (Line 167) const dq = EUDDeque(7)();
dq = _CGFW(lambda: [EUDDeque(7)()], 1)[0]
# (Line 168) function test_deque() {
@EUDFunc
def f_test_deque():
    # (Line 169) const ret = py_list();
    ret = list()
    # (Line 170) var pushes = 1;
    pushes = _LVAR([1])
    # (Line 171) const a = function () { dq.append(pushes); pushes++; };
    @EUDFunc
    def _lambda1():
        dq.append(pushes)
        pushes.__iadd__(1)

    a = _lambda1
    # (Line 172) const aL = function () { dq.appendleft(pushes); pushes++; };
    @EUDFunc
    def _lambda2():
        dq.appendleft(pushes)
        pushes.__iadd__(1)

    aL = _lambda2
    # (Line 173) const _p = function() { if (dq.empty()) return 0; else return dq.pop(); };
    @EUDFunc
    def _lambda3():
        if EUDIf()(dq.empty()):
            EUDReturn(0)
        if EUDElse()():
            EUDReturn(dq.pop())
        EUDEndIf()

    _p = _lambda3
    # (Line 174) const _pL = function() { if (dq.empty()) return 0; else return dq.popleft(); };
    @EUDFunc
    def _lambda4():
        if EUDIf()(dq.empty()):
            EUDReturn(0)
        if EUDElse()():
            EUDReturn(dq.popleft())
        EUDEndIf()

    _pL = _lambda4
    # (Line 175) const p = py_eval('lambda s=ret, f=_p: s.append(f())');
    p = eval('lambda s=ret, f=_p: s.append(f())')
    # (Line 176) const pL = py_eval('lambda s=ret, f=_pL: s.append(f())');
    pL = eval('lambda s=ret, f=_pL: s.append(f())')
    # (Line 177) const methodMap = py_eval('{\
    # (Line 180) }');
    methodMap = eval('{        "append":     a,    "pop":     p,        "appendleft": aL,   "popleft": pL,    }')
    # (Line 181) foreach(method : DequeCases) { methodMap[method](); }
    for method in DequeCases:
        _ARRC(methodMap, method)()
        # (Line 182) var sum = dq.length;

    sum = _LVAR([dq.length])
    # (Line 183) foreach(element: dq) { sum += element; }
    for element in dq:
        sum.__iadd__(element)
        # (Line 184) ret.append(sum);

    ret.append(sum)
    # (Line 185) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 186) }
