## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH
# (Line 1) object Test {
# (Line 2) var x, y, z;
class Test(EUDStruct):
    # (Line 3) function setX(x) { this.x = x; }
    @EUDMethod
    def setX(this, x):
        _ATTW(this, 'x') << (x)
        # (Line 4) function add(other: selftype) {

    @EUDTypedMethod([selftype])
    def add(this, other):
        # (Line 5) this.x += other.x;
        _ATTW(this, 'x').__iadd__(other.x)
        # (Line 6) this.y += other.y;
        _ATTW(this, 'y').__iadd__(other.y)
        # (Line 7) this.z += other.z;
        _ATTW(this, 'z').__iadd__(other.z)
        # (Line 8) }
        # (Line 9) };

    # (Line 10) function test_object() {
    _fields_ = [
        'x',
        'y',
        'z',
    ]

@EUDFunc
def f_test_object():
    # (Line 11) const a = Test();
    a = Test()
    # (Line 12) a.x, a.y = 5, 7;
    _SV([_ATTW(a, 'x'), _ATTW(a, 'y')], [5, 7])
    # (Line 14) const b = Test.cast(a);
    b = Test.cast(a)
    # (Line 15) const c = Test.cast(b);
    c = Test.cast(b)
    # (Line 17) b.z = 8;
    _ATTW(b, 'z') << (8)
    # (Line 18) c.x = 3;
    _ATTW(c, 'x') << (3)
    # (Line 21) var ret = a ? 1 : 0;
    ret = _LVAR([EUDTernary(a)(1)(0)])
    # (Line 22) if (a.x == b.x && b.x == c.x) ret += 2;
    if EUDIf()(EUDSCAnd()(_ATTC(a, 'x') == b.x)(_ATTC(b, 'x') == c.x)()):
        ret.__iadd__(2)
        # (Line 23) if (a.y == b.y && b.y == c.y) ret += 4;
    EUDEndIf()
    if EUDIf()(EUDSCAnd()(_ATTC(a, 'y') == b.y)(_ATTC(b, 'y') == c.y)()):
        ret.__iadd__(4)
        # (Line 24) if (a.z == b.z && b.z == c.z) ret += 8;
    EUDEndIf()
    if EUDIf()(EUDSCAnd()(_ATTC(a, 'z') == b.z)(_ATTC(b, 'z') == c.z)()):
        ret.__iadd__(8)
        # (Line 25) if (a.x == 3 && b.y == 7 && c.z == 8) ret += 16;
    EUDEndIf()
    if EUDIf()(EUDSCAnd()(_ATTC(a, 'x') == 3)(_ATTC(b, 'y') == 7)(_ATTC(c, 'z') == 8)()):
        ret.__iadd__(16)
        # (Line 27) const d = a.copy();
    EUDEndIf()
    d = a.copy()
    # (Line 28) a.add(d);
    a.add(d)
    # (Line 29) if (c.x == 6 && a.y == 14 && b.z == 16) ret += 32;
    if EUDIf()(EUDSCAnd()(_ATTC(c, 'x') == 6)(_ATTC(a, 'y') == 14)(_ATTC(b, 'z') == 16)()):
        ret.__iadd__(32)
        # (Line 30) if (d.x == 3 && d.y == 7 && d.z == 8) ret += 64;
    EUDEndIf()
    if EUDIf()(EUDSCAnd()(_ATTC(d, 'x') == 3)(_ATTC(d, 'y') == 7)(_ATTC(d, 'z') == 8)()):
        ret.__iadd__(64)
        # (Line 32) var e = a;
    EUDEndIf()
    e = _LVAR([a])
    # (Line 33) Test.cast(e).setX(1);
    Test.cast(e).setX(1)
    # (Line 34) if (a.x == 1) ret += 128;
    if EUDIf()(_ATTC(a, 'x') == 1):
        ret.__iadd__(128)
        # (Line 35) Test.cast(e).add(d);
    EUDEndIf()
    Test.cast(e).add(d)
    # (Line 36) if (b.x == 4 && c.y == 21 && a.z == 24) ret += 256;
    if EUDIf()(EUDSCAnd()(_ATTC(b, 'x') == 4)(_ATTC(c, 'y') == 21)(_ATTC(a, 'z') == 24)()):
        ret.__iadd__(256)
        # (Line 38) return ret;  // 511
    EUDEndIf()
    EUDReturn(ret)
    # (Line 39) }
    # (Line 41) object Coord { var x, y; };

class Coord(EUDStruct):
    # (Line 42) object Triangle {
    _fields_ = [
        'x',
        'y',
    ]

# (Line 43) var p: Coord * 5;
class Triangle(EUDStruct):
    # (Line 44) var q;
    # (Line 45) };
    # (Line 46) function test_nested_object() {
    _fields_ = [
        ('p', Coord * 5),
        'q',
    ]

@EUDFunc
def f_test_nested_object():
    # (Line 47) const a = Triangle();
    a = Triangle()
    # (Line 48) a.p = (Coord * 5)();
    _ATTW(a, 'p') << ((Coord * 5)())
    # (Line 49) foreach(i : py_range(5)) {
    for i in range(5):
        # (Line 50) a.p[i] = Coord();
        _ARRW(a.p, i) << (Coord())
        # (Line 51) }
        # (Line 53) a.p[0].x = 1;

    _ATTW(a.p[0], 'x') << (1)
    # (Line 54) a.p[1].y = 2;
    _ATTW(a.p[1], 'y') << (2)
    # (Line 55) a.p[1].y += 2;
    _ATTW(a.p[1], 'y').__iadd__(2)
    # (Line 56) a.q = 3;
    _ATTW(a, 'q') << (3)
    # (Line 58) var ret = list(a.p[0].x == 1, a.p[0].y == 0, a.p[1].y == 4, a.q == 3) ? 1 : 0;
    ret = _LVAR([EUDTernary(FlattenList([_ATTC(a.p[0], 'x') == 1, _ATTC(a.p[0], 'y') == 0, _ATTC(a.p[1], 'y') == 4, _ATTC(a, 'q') == 3]))(1)(0)])
    # (Line 60) const b = a.copy();
    b = a.copy()
    # (Line 61) b.p[0].x = 5;
    _ATTW(b.p[0], 'x') << (5)
    # (Line 62) b.q = 2;
    _ATTW(b, 'q') << (2)
    # (Line 63) if (a.p[0].x == 5) ret += 2;
    if EUDIf()(_ATTC(a.p[0], 'x') == 5):
        ret.__iadd__(2)
        # (Line 64) if (b.p[0].x == 5) ret += 4;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[0], 'x') == 5):
        ret.__iadd__(4)
        # (Line 65) if (b.p[0].y == 0) ret += 8;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[0], 'y') == 0):
        ret.__iadd__(8)
        # (Line 66) if (b.p[1].y == 4) ret += 16;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[1], 'y') == 4):
        ret.__iadd__(16)
        # (Line 67) if (a.q == 3) ret += 32;
    EUDEndIf()
    if EUDIf()(_ATTC(a, 'q') == 3):
        ret.__iadd__(32)
        # (Line 68) if (b.q == 2) ret += 64;
    EUDEndIf()
    if EUDIf()(_ATTC(b, 'q') == 2):
        ret.__iadd__(64)
        # (Line 70) return ret;
    EUDEndIf()
    EUDReturn(ret)
    # (Line 71) }
    # (Line 73) const ListList = py_list();

ListList = _CGFW(lambda: [list()], 1)[0]
# (Line 74) var AllList;  // EUDArray
AllList = EUDVariable()
# (Line 75) object List {
# (Line 76) var prev: selftype, next: selftype;
class List(EUDStruct):
    # (Line 77) function constructor() {
    @EUDMethod
    def constructor(this):
        # (Line 78) py_exec("\
        # (Line 84) EUDOnStart(init)");
        exec("if not ListList:\n    def init():\n        global AllList\n        ListList.append(-1)\n        AllList << EUDArray(ListList)\n    EUDOnStart(init)")
        # (Line 85) ListList.append(this);
        ListList.append(this)
        # (Line 86) }
        # (Line 87) function foo(c: Coord) {}

    @EUDTypedMethod([Coord])
    def foo(this, c):
        # (Line 88) };
        pass

    # (Line 89) function test_selftype_member() {
    _fields_ = [
        ('prev', selftype),
        ('next', selftype),
    ]

@EUDFunc
def f_test_selftype_member():
    # (Line 90) const a, b = List(), List();
    a, b = List2Assignable([List(), List()])
    # (Line 91) a.prev = b;
    _ATTW(a, 'prev') << (b)
    # (Line 92) a.next = b;
    _ATTW(a, 'next') << (b)
    # (Line 93) b.prev = a;
    _ATTW(b, 'prev') << (a)
    # (Line 94) b.next = a;
    _ATTW(b, 'next') << (a)
    # (Line 95) a.foo(0);
    a.foo(0)
    # (Line 96) const c = List();
    c = List()
    # (Line 97) const d = List();
    d = List()
    # (Line 98) const e = List();
    e = List()
    # (Line 100) const arr = EUDArray.cast(AllList);
    arr = EUDArray.cast(AllList)
    # (Line 101) var i;
    i = EUDVariable()
    # (Line 102) for (i = 0 ; arr[i] != -1 ; i++) {}
    i << (0)
    if EUDWhile()(_ARRC(arr, i) == -1, neg=True):
        def _t2():
            i.__iadd__(1)
        # (Line 103) return i;
        EUDSetContinuePoint()
        _t2()
    EUDEndWhile()
    EUDReturn(i)
    # (Line 104) }
    # (Line 106) object RandomData {

# (Line 107) var arr: EUDArray;
class RandomData(EUDStruct):
    # (Line 108) var count;
    # (Line 110) function constructor(arr, count) {
    @EUDMethod
    def constructor(this, arr, count):
        # (Line 111) this.arr = arr;
        _ATTW(this, 'arr') << (arr)
        # (Line 112) this.count = count;
        _ATTW(this, 'count') << (count)
        # (Line 113) }
        # (Line 115) function get_value() {

    @EUDMethod
    def get_value(this):
        # (Line 116) return this.arr[dwrand() % this.count];
        EUDReturn(this.arr[f_dwrand() % this.count])
        # (Line 117) }
        # (Line 118) };

    # (Line 119) function test_eudmethods() {
    _fields_ = [
        ('arr', EUDArray),
        'count',
    ]

@EUDFunc
def f_test_eudmethods():
    # (Line 120) const rd = RandomData(EUDArray(list(1,2,3,4,5,6,7)), 7);
    rd = RandomData(EUDArray(FlattenList([1, 2, 3, 4, 5, 6, 7])), 7)
    # (Line 121) var ret = 0;
    ret = _LVAR([0])
    # (Line 122) foreach(n : py_range(7)) {
    for n in range(7):
        # (Line 123) const v = rd.get_value();
        v = rd.get_value()
        # (Line 124) if (1 <= v && v <= 7) ret += 1;
        if EUDIf()(EUDSCAnd()(1 <= v)(v <= 7)()):
            ret.__iadd__(1)
            # (Line 125) }
        EUDEndIf()
        # (Line 126) return ret;

    EUDReturn(ret)
    # (Line 127) }
