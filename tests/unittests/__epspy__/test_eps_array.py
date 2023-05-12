## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH
# (Line 1) import py_random;
import random
# (Line 2) import py_itertools;
import itertools
# (Line 3) import collections.deque;
from collections import deque
# (Line 4) const testArray = [1, 2, 3, 4];
testArray = _CGFW(lambda: [_ARR(FlattenList([1, 2, 3, 4]))], 1)[0]
# (Line 5) function test_write() {
@EUDFunc
def f_test_write():
    # (Line 6) const ret = py_list();
    ret = list()
    # (Line 8) const u32 = py_eval("lambda: random.randint(1, 0xFFFFFFFF)");
    u32 = eval("lambda: random.randint(1, 0xFFFFFFFF)")
    # (Line 9) const shift = py_eval("lambda: random.randint(0, 31)");
    shift = eval("lambda: random.randint(0, 31)")
    # (Line 11) const num = u32(), u32(), u32(), u32(), u32(), u32(),
    # (Line 12) shift(), shift(), u32(), u32(), u32();
    num = u32(), u32(), u32(), u32(), u32(), u32(), shift(), shift(), u32(), u32(), u32()
    # (Line 13) const numV = EUDArray(num);
    numV = EUDArray(num)
    # (Line 14) const numS = num, numV;
    numS = num, numV
    # (Line 15) setcurpl(getuserplayerid());
    f_setcurpl(f_getuserplayerid())
    # (Line 16) const dbg = StringBuffer(3000);
    dbg = StringBuffer(3000)
    # (Line 17) dbg.insert(0);
    dbg.insert(0)
    # (Line 18) foreach(vals : numS) {
    for vals in numS:
        # (Line 19) var expect = vals[0];
        expect = _LVAR([vals[0]])
        # (Line 20) expect += vals[1];
        expect.__iadd__(vals[1])
        # (Line 21) expect -= vals[2];
        expect.__isub__(vals[2])
        # (Line 22) dbg.appendf("\n\x07{:x}\x02 *= {:x}", expect, vals[3],);
        dbg.appendf("\n\x07{:x}\x02 *= {:x}", expect, vals[3])
        # (Line 23) expect *= vals[3];
        expect.__imul__(vals[3])
        # (Line 24) var temp = expect;
        temp = _LVAR([expect])
        # (Line 25) dbg.appendf(" -> \x07{:x}\x02 /= {:x}", expect, vals[4],);
        dbg.appendf(" -> \x07{:x}\x02 /= {:x}", expect, vals[4])
        # (Line 26) expect /= vals[4];
        expect.__ifloordiv__(vals[4])
        # (Line 27) temp += expect;
        temp.__iadd__(expect)
        # (Line 28) dbg.appendf(" -> \x07{}\x02 %= {:x}", expect, vals[5],);
        dbg.appendf(" -> \x07{}\x02 %= {:x}", expect, vals[5])
        # (Line 29) expect %= vals[5];
        expect.__imod__(vals[5])
        # (Line 30) temp += expect;
        temp.__iadd__(expect)
        # (Line 31) dbg.appendf(" -> \x07{}\x02 <<= {}", expect, vals[6],);
        dbg.appendf(" -> \x07{}\x02 <<= {}", expect, vals[6])
        # (Line 32) expect <<= vals[6];
        expect.__ilshift__(vals[6])
        # (Line 33) temp += expect;
        temp.__iadd__(expect)
        # (Line 34) dbg.appendf(" -> \x07{:x}\x02 >>= {}", expect, vals[7],);
        dbg.appendf(" -> \x07{:x}\x02 >>= {}", expect, vals[7])
        # (Line 35) expect >>= vals[7];
        expect.__irshift__(vals[7])
        # (Line 36) temp += expect;
        temp.__iadd__(expect)
        # (Line 39) dbg.appendf(" -> \x07{}\x02 &= {:x}", expect, vals[8]);
        dbg.appendf(" -> \x07{}\x02 &= {:x}", expect, vals[8])
        # (Line 40) expect &= vals[8];
        expect.__iand__(vals[8])
        # (Line 41) temp += expect;
        temp.__iadd__(expect)
        # (Line 42) dbg.appendf(" -> \x07{}\x02 |= {:x}", expect, vals[9]);
        dbg.appendf(" -> \x07{}\x02 |= {:x}", expect, vals[9])
        # (Line 43) expect |= vals[9];
        expect.__ior__(vals[9])
        # (Line 44) temp += expect;
        temp.__iadd__(expect)
        # (Line 45) dbg.appendf(" -> \x07{:x}", expect);
        dbg.appendf(" -> \x07{:x}", expect)
        # (Line 46) expect ^= vals[10];
        expect.__ixor__(vals[10])
        # (Line 47) temp += expect;
        temp.__iadd__(expect)
        # (Line 48) ret.append(temp);
        ret.append(temp)
        # (Line 49) }
        # (Line 50) const pvar, arr = PVariable(), EUDArray(8);

    pvar, arr = List2Assignable([PVariable(), EUDArray(8)])
    # (Line 51) var v1, v2 = pvar, arr;
    v1, v2 = _LVAR([pvar, arr])
    # (Line 52) const pvarV, arrV = PVariable.cast(v1), EUDArray.cast(v2);
    pvarV, arrV = List2Assignable([PVariable.cast(v1), EUDArray.cast(v2)])
    # (Line 54) const index = py_eval("random.randint(0, 7)");
    index = eval("random.randint(0, 7)")
    # (Line 55) var indexV = index;
    indexV = _LVAR([index])
    # (Line 57) foreach(arr, i, vals : py_eval("itertools.product(\
    # (Line 59) )")) {
    for arr_1, i, vals in eval("itertools.product(        (pvar, arr, pvarV, arrV), (index, indexV), (num, numV)    )"):
        # (Line 60) arr[i] = vals[0];
        _ARRW(arr_1, i) << (vals[0])
        # (Line 61) arr[i] += vals[1];
        _ARRW(arr_1, i).__iadd__(vals[1])
        # (Line 62) arr[i] -= vals[2];
        _ARRW(arr_1, i).__isub__(vals[2])
        # (Line 63) arr[i] *= vals[3];
        _ARRW(arr_1, i).__imul__(vals[3])
        # (Line 64) var temp = arr[i];
        temp = _LVAR([arr_1[i]])
        # (Line 65) arr[i] /= vals[4];
        _ARRW(arr_1, i).__ifloordiv__(vals[4])
        # (Line 66) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 67) arr[i] %= vals[5];
        _ARRW(arr_1, i).__imod__(vals[5])
        # (Line 68) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 69) arr[i] <<= vals[6];
        _ARRW(arr_1, i).__ilshift__(vals[6])
        # (Line 70) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 71) arr[i] >>= vals[7];
        _ARRW(arr_1, i).__irshift__(vals[7])
        # (Line 72) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 75) arr[i] &= vals[8];
        _ARRW(arr_1, i).__iand__(vals[8])
        # (Line 76) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 77) arr[i] |= vals[9];
        _ARRW(arr_1, i).__ior__(vals[9])
        # (Line 78) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 79) arr[i] ^= vals[10];
        _ARRW(arr_1, i).__ixor__(vals[10])
        # (Line 80) temp += arr[i];
        temp.__iadd__(arr_1[i])
        # (Line 81) ret.append(temp);
        ret.append(temp)
        # (Line 82) }
        # (Line 83) dbg.Display();

    dbg.Display()
    # (Line 85) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 86) }
    # (Line 87) function test_compare() {

@EUDFunc
def f_test_compare():
    # (Line 88) const ret = py_list();
    ret = list()
    # (Line 89) const num = py_eval("[random.randint(1, 0xFFFFFFFF) for _ in range(11)]");
    num = eval("[random.randint(1, 0xFFFFFFFF) for _ in range(11)]")
    # (Line 90) const numV = EUDArray(num);
    numV = EUDArray(num)
    # (Line 92) const pvar, arr = PVariable(), EUDArray(8);
    pvar, arr = List2Assignable([PVariable(), EUDArray(8)])
    # (Line 93) var v1, v2 = pvar, arr;
    v1, v2 = _LVAR([pvar, arr])
    # (Line 94) const pvarV, arrV = PVariable.cast(v1), EUDArray.cast(v2);
    pvarV, arrV = List2Assignable([PVariable.cast(v1), EUDArray.cast(v2)])
    # (Line 96) const index = py_eval("random.randint(0, 7)");
    index = eval("random.randint(0, 7)")
    # (Line 97) var indexV = index;
    indexV = _LVAR([index])
    # (Line 99) foreach(arr, i, vals : py_eval("itertools.product(\
    # (Line 101) )")) {
    for arr_1, i, vals in eval("itertools.product(        (pvar, arr, pvarV, arrV), (index, indexV), (num, numV)    )"):
        # (Line 102) var temp = 0;
        temp = _LVAR([0])
        # (Line 103) arr[i] = vals[0];
        _ARRW(arr_1, i) << (vals[0])
        # (Line 104) if (arr[i] == vals[1]) temp += 1 << 1;
        if EUDIf()(_ARRC(arr_1, i) == vals[1]):
            temp.__iadd__(_LSH(1,1))
            # (Line 105) if (arr[i] != vals[2]) temp += 1 << 2;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) == vals[2], neg=True):
            temp.__iadd__(_LSH(1,2))
            # (Line 106) if (arr[i] >= vals[3]) temp += 1 << 3;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) >= vals[3]):
            temp.__iadd__(_LSH(1,3))
            # (Line 107) if (arr[i] <= vals[4]) temp += 1 << 4;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) <= vals[4]):
            temp.__iadd__(_LSH(1,4))
            # (Line 108) if (arr[i] > vals[5]) temp += 1 << 5;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) <= vals[5], neg=True):
            temp.__iadd__(_LSH(1,5))
            # (Line 109) if (arr[i] < vals[6]) temp += 1 << 6;
        EUDEndIf()
        if EUDIf()(_ARRC(arr_1, i) >= vals[6], neg=True):
            temp.__iadd__(_LSH(1,6))
            # (Line 110) ret.append(temp);
        EUDEndIf()
        ret.append(temp)
        # (Line 111) }
        # (Line 113) return List2Assignable(ret);

    EUDReturn(List2Assignable(ret))
    # (Line 114) }
    # (Line 115) const q8 = EUDQueue(8)();

q8 = _CGFW(lambda: [EUDQueue(8)()], 1)[0]
# (Line 116) function test_queue() {
@EUDFunc
def f_test_queue():
    # (Line 117) var ret = 0;
    ret = _LVAR([0])
    # (Line 118) ret += q8.empty() ? 0b1 : 0;  // ret = 1
    ret.__iadd__(EUDTernary(q8.empty())(0b1)(0))
    # (Line 119) q8.append(1);
    q8.append(1)
    # (Line 120) q8.append(EUDVariable(2));
    q8.append(EUDVariable(2))
    # (Line 121) ret += 1 << q8.popleft();  // pop 1, ret = 3
    ret.__iadd__(_LSH(1,q8.popleft()))
    # (Line 122) q8.append(EUDVariable(3));
    q8.append(EUDVariable(3))
    # (Line 123) ret += q8.empty() ? 0x80000000 : 0;
    ret.__iadd__(EUDTernary(q8.empty())(0x80000000)(0))
    # (Line 124) ret += q8.popleft() == 2 ? 0b100 : 0;  // pop 2, ret = 7
    ret.__iadd__(EUDTernary(q8.popleft() == 2)(0b100)(0))
    # (Line 125) ret += q8.popleft() == 3 ? 0b1000 : 0;  // pop 3, ret = 15
    ret.__iadd__(EUDTernary(q8.popleft() == 3)(0b1000)(0))
    # (Line 126) ret += q8.empty() ? 0b10000 : 0;  // ret = 31
    ret.__iadd__(EUDTernary(q8.empty())(0b10000)(0))
    # (Line 127) return ret;
    EUDReturn(ret)
    # (Line 128) }
    # (Line 129) function test_queue_wraparound() {

@EUDFunc
def f_test_queue_wraparound():
    # (Line 130) const q3 = EUDQueue(3)();
    q3 = EUDQueue(3)()
    # (Line 131) const ret = EUDCreateVariables(6);
    ret = EUDCreateVariables(6)
    # (Line 132) var iter = 0;
    iter = _LVAR([0])
    # (Line 134) foreach(v : q3) { ret[0] += v; iter++; }
    for v in q3:
        _ARRW(ret, 0).__iadd__(v)
        iter.__iadd__(1)
        # (Line 135) q3.append(1);

    q3.append(1)
    # (Line 136) q3.append(2);
    q3.append(2)
    # (Line 138) foreach(v : q3) { ret[1] += v; iter++; }
    for v in q3:
        _ARRW(ret, 1).__iadd__(v)
        iter.__iadd__(1)
        # (Line 139) q3.append(3);

    q3.append(3)
    # (Line 140) q3.append(4);
    q3.append(4)
    # (Line 142) foreach(v : q3) { ret[2] += v; iter++; }
    for v in q3:
        _ARRW(ret, 2).__iadd__(v)
        iter.__iadd__(1)
        # (Line 143) q3.append(5);

    q3.append(5)
    # (Line 145) foreach(v : q3) { ret[3] += v; iter++; }
    for v in q3:
        _ARRW(ret, 3).__iadd__(v)
        iter.__iadd__(1)
        # (Line 146) q3.popleft();

    q3.popleft()
    # (Line 148) foreach(v : q3) { ret[4] += v; iter++; }
    for v in q3:
        _ARRW(ret, 4).__iadd__(v)
        iter.__iadd__(1)
        # (Line 149) q3.append(6);

    q3.append(6)
    # (Line 150) q3.append(7);
    q3.append(7)
    # (Line 152) foreach(v : q3) {
    for v in q3:
        # (Line 153) if (v == 5) continue;
        if EUDIf()(v == 5):
            EUDContinue()
            # (Line 154) ret[5] += v;
        EUDEndIf()
        _ARRW(ret, 5).__iadd__(v)
        # (Line 155) EUDSetContinuePoint();
        EUDSetContinuePoint()
        # (Line 156) iter++;
        iter.__iadd__(1)
        # (Line 157) }
        # (Line 158) q3.append(8);

    q3.append(8)
    # (Line 159) q3.append(9);
    q3.append(9)
    # (Line 160) foreach(v : q3) {
    for v in q3:
        # (Line 161) if (v == 8) break;
        if EUDIf()(v == 8):
            EUDBreak()
            # (Line 162) ret[5] += v; iter++;
        EUDEndIf()
        _ARRW(ret, 5).__iadd__(v)
        iter.__iadd__(1)
        # (Line 163) }
        # (Line 164) ret.append(iter);

    ret.append(iter)
    # (Line 165) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 166) }
    # (Line 167) const methods = py_eval('{\

# (Line 170) }');
methods = _CGFW(lambda: [eval('{    "append": "a",   "appendleft": "aL",    "pop":    "p",   "popleft":    "pL"}')], 1)[0]
# (Line 171) const DequeCases = py_eval('random.sample(sorted(methods), 27, counts=[9, 9, 9, 9])');
DequeCases = _CGFW(lambda: [eval('random.sample(sorted(methods), 27, counts=[9, 9, 9, 9])')], 1)[0]
# (Line 172) const DequeTest = py_eval("''.join(methods[name] for name in DequeCases)");
DequeTest = _CGFW(lambda: [eval("''.join(methods[name] for name in DequeCases)")], 1)[0]
# (Line 173) const dq = EUDDeque(7)();
dq = _CGFW(lambda: [EUDDeque(7)()], 1)[0]
# (Line 174) function test_deque() {
@EUDFunc
def f_test_deque():
    # (Line 175) const ret = py_list();
    ret = list()
    # (Line 176) var pushes = 1;
    pushes = _LVAR([1])
    # (Line 177) const a = function () { dq.append(pushes); pushes++; };
    @EUDFunc
    def _lambda1():
        dq.append(pushes)
        pushes.__iadd__(1)

    a = _lambda1
    # (Line 178) const aL = function () { dq.appendleft(pushes); pushes++; };
    @EUDFunc
    def _lambda2():
        dq.appendleft(pushes)
        pushes.__iadd__(1)

    aL = _lambda2
    # (Line 179) const _p = function() { if (dq.empty()) return 0; else return dq.pop(); };
    @EUDFunc
    def _lambda3():
        if EUDIf()(dq.empty()):
            EUDReturn(0)
        if EUDElse()():
            EUDReturn(dq.pop())
        EUDEndIf()

    _p = _lambda3
    # (Line 180) const _pL = function() { if (dq.empty()) return 0; else return dq.popleft(); };
    @EUDFunc
    def _lambda4():
        if EUDIf()(dq.empty()):
            EUDReturn(0)
        if EUDElse()():
            EUDReturn(dq.popleft())
        EUDEndIf()

    _pL = _lambda4
    # (Line 181) const p = py_eval('lambda s=ret, f=_p: s.append(f())');
    p = eval('lambda s=ret, f=_p: s.append(f())')
    # (Line 182) const pL = py_eval('lambda s=ret, f=_pL: s.append(f())');
    pL = eval('lambda s=ret, f=_pL: s.append(f())')
    # (Line 183) const methodMap = py_eval('{\
    # (Line 186) }');
    methodMap = eval('{        "append":     a,    "pop":     p,        "appendleft": aL,   "popleft": pL,    }')
    # (Line 187) foreach(method : DequeCases) { methodMap[method](); }
    for method in DequeCases:
        methodMap[method]()
        # (Line 188) var sum = dq.length;

    sum = _LVAR([dq.length])
    # (Line 189) foreach(element: dq) { sum += element; }
    for element in dq:
        sum.__iadd__(element)
        # (Line 190) ret.append(sum);

    ret.append(sum)
    # (Line 191) return List2Assignable(ret);
    EUDReturn(List2Assignable(ret))
    # (Line 192) }
