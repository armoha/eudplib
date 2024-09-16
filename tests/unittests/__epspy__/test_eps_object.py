## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL
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
    ret = _TYLV([None], [EUDTernary(a)(1)(0)])
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
    e = _TYLV([None], [a])
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
    # (Line 41) object Triangle;

# (Line 42) object Coord { var x, y; };
class Coord(EUDStruct):
    # (Line 43) object Triangle {
    _fields_ = [
        'x',
        'y',
    ]

# (Line 44) var p: Coord * 5;
class Triangle(EUDStruct):
    # (Line 45) var q;
    # (Line 46) };
    # (Line 48) function test_nested_object() {
    _fields_ = [
        ('p', Coord * 5),
        'q',
    ]

@EUDFunc
def f_test_nested_object():
    # (Line 49) const a = Triangle();
    a = Triangle()
    # (Line 50) a.p = (Coord * 5)();
    _ATTW(a, 'p') << ((Coord * 5)())
    # (Line 51) foreach(i : py_range(5)) {
    for i in range(5):
        # (Line 52) a.p[i] = Coord();
        _ARRW(a.p, i) << (Coord())
        # (Line 53) }
        # (Line 55) a.p[0].x = 1;

    _ATTW(a.p[0], 'x') << (1)
    # (Line 56) a.p[1].y = 2;
    _ATTW(a.p[1], 'y') << (2)
    # (Line 57) a.p[1].y += 2;
    _ATTW(a.p[1], 'y').__iadd__(2)
    # (Line 58) a.q = 3;
    _ATTW(a, 'q') << (3)
    # (Line 60) var ret = list(a.p[0].x == 1, a.p[0].y == 0, a.p[1].y == 4, a.q == 3) ? 1 : 0;
    ret = _TYLV([None], [EUDTernary(FlattenList([_ATTC(a.p[0], 'x') == 1, _ATTC(a.p[0], 'y') == 0, _ATTC(a.p[1], 'y') == 4, _ATTC(a, 'q') == 3]))(1)(0)])
    # (Line 62) const b = a.copy();
    b = a.copy()
    # (Line 63) b.p[0].x = 5;
    _ATTW(b.p[0], 'x') << (5)
    # (Line 64) b.q = 2;
    _ATTW(b, 'q') << (2)
    # (Line 65) if (a.p[0].x == 5) ret += 2;
    if EUDIf()(_ATTC(a.p[0], 'x') == 5):
        ret.__iadd__(2)
        # (Line 66) if (b.p[0].x == 5) ret += 4;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[0], 'x') == 5):
        ret.__iadd__(4)
        # (Line 67) if (b.p[0].y == 0) ret += 8;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[0], 'y') == 0):
        ret.__iadd__(8)
        # (Line 68) if (b.p[1].y == 4) ret += 16;
    EUDEndIf()
    if EUDIf()(_ATTC(b.p[1], 'y') == 4):
        ret.__iadd__(16)
        # (Line 69) if (a.q == 3) ret += 32;
    EUDEndIf()
    if EUDIf()(_ATTC(a, 'q') == 3):
        ret.__iadd__(32)
        # (Line 70) if (b.q == 2) ret += 64;
    EUDEndIf()
    if EUDIf()(_ATTC(b, 'q') == 2):
        ret.__iadd__(64)
        # (Line 72) return ret;
    EUDEndIf()
    EUDReturn(ret)
    # (Line 73) }
    # (Line 75) var ListCount = 0;

ListCount = _TYGV([None], lambda: [0])
# (Line 76) object List {
# (Line 77) var prev: selftype, next: selftype;
class List(EUDStruct):
    # (Line 78) function constructor() {
    @EUDMethod
    def constructor(this):
        # (Line 79) ListCount += 1;
        ListCount.__iadd__(1)
        # (Line 80) }
        # (Line 81) function foo(c: Coord) {}

    @EUDTypedMethod([Coord])
    def foo(this, c):
        # (Line 82) };
        pass

    # (Line 83) function test_selftype_member() {
    _fields_ = [
        ('prev', selftype),
        ('next', selftype),
    ]

@EUDFunc
def f_test_selftype_member():
    # (Line 84) const a, b = List(), List();
    a, b = List2Assignable([List(), List()])
    # (Line 85) a.prev = b;
    _ATTW(a, 'prev') << (b)
    # (Line 86) a.next = b;
    _ATTW(a, 'next') << (b)
    # (Line 87) b.prev = a;
    _ATTW(b, 'prev') << (a)
    # (Line 88) b.next = a;
    _ATTW(b, 'next') << (a)
    # (Line 89) a.foo(0);
    a.foo(0)
    # (Line 90) const c = List();
    c = List()
    # (Line 91) const d = List();
    d = List()
    # (Line 92) const e = List();
    e = List()
    # (Line 94) return ListCount;
    EUDReturn(ListCount)
    # (Line 95) }
    # (Line 97) object RandomData {

# (Line 98) var arr: EUDArray;
class RandomData(EUDStruct):
    # (Line 99) var count;
    # (Line 101) function constructor(arr, count) {
    @EUDMethod
    def constructor(this, arr, count):
        # (Line 102) this.arr = arr;
        _ATTW(this, 'arr') << (arr)
        # (Line 103) this.count = count;
        _ATTW(this, 'count') << (count)
        # (Line 104) }
        # (Line 106) function get_value() {

    @EUDMethod
    def get_value(this):
        # (Line 107) return this.arr[dwrand() % this.count];
        EUDReturn(this.arr[f_dwrand() % this.count])
        # (Line 108) }
        # (Line 109) };

    # (Line 110) function test_eudmethods() {
    _fields_ = [
        ('arr', EUDArray),
        'count',
    ]

@EUDFunc
def f_test_eudmethods():
    # (Line 111) const rd = RandomData(EUDArray(list(1,2,3,4,5,6,7)), 7);
    rd = RandomData(EUDArray(FlattenList([1, 2, 3, 4, 5, 6, 7])), 7)
    # (Line 112) var ret = 0;
    ret = _TYLV([None], [0])
    # (Line 113) foreach(n : py_range(7)) {
    for n in range(7):
        # (Line 114) const v = rd.get_value();
        v = rd.get_value()
        # (Line 115) if (1 <= v && v <= 7) ret += 1;
        if EUDIf()(EUDSCAnd()(1 <= v)(v <= 7)()):
            ret.__iadd__(1)
            # (Line 116) }
        EUDEndIf()
        # (Line 117) return ret;

    EUDReturn(ret)
    # (Line 118) }
