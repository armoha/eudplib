## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH, _ALL
# (Line 1) function test_cunit1() {
@EUDFunc
def f_test_cunit1():
    # (Line 2) const sp = [0x2468ACE0, 0x13579BDF, 0xFEDCBA98, 0x76543210];
    sp = _ARR(FlattenList([0x2468ACE0, 0x13579BDF, 0xFEDCBA98, 0x76543210]))
    # (Line 3) const a = [
    # (Line 4) 0,  -1,  -2,  sp,  -4,  -5,  -6,  -7,  -8, -9,
    # (Line 5) -10, -11, -12, -13, -14, -15, -16, -17, -18, 0x12345607,
    # (Line 6) 0x89ABCDEF, 0xEDACEDAC, 0xEDACEDAC, 0xEDACEDAC, 0x220011, 0x440033, 0xFFFF0055, 0, 0, 0,
    # (Line 7) 3, 3, 3, 3, 3, 3, 3, 3, 0x220011, 0x440033,
    # (Line 8) 0xFFFF0055, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    # (Line 9) 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
    # (Line 10) ];
    a = _ARR(FlattenList([0, -1, -2, sp, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, 0x12345607, 0x89ABCDEF, 0xEDACEDAC, 0xEDACEDAC, 0xEDACEDAC, 0x220011, 0x440033, 0xFFFF0055, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0x220011, 0x440033, 0xFFFF0055, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]))
    # (Line 11) const u = CUnit(EUDVariable(EPD(a)));
    u = CUnit(EUDVariable(EPD(a)))
    # (Line 12) py_exec("\n\
    # (Line 16) ");
    exec("\nfrom helper import expect_error\nwith expect_error(AttributeError):\n    u.zzt = 1\n")
    # (Line 17) var ret = 0;
    ret = _LVAR([0])
    # (Line 18) if (u.order == 0x56) ret += 1;
    if EUDIf()(_ATTC(u, 'order') == 0x56):
        ret.__iadd__(1)
        # (Line 19) if (u.owner == P8) ret += 2;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'owner') == P8):
        ret.__iadd__(2)
        # (Line 20) if (u.orderState == 0x34) ret += 4;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderState') == 0x34):
        ret.__iadd__(4)
        # (Line 21) if (u.orderSignal == 0x12) ret += 8;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderSignal') == 0x12):
        ret.__iadd__(8)
        # (Line 23) if (u.orderUnitType == 0xCDEF) ret += 16;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderUnitType') == 0xCDEF):
        ret.__iadd__(16)
        # (Line 24) wwrite_epd(EPD(a) + 0x50/4, 0, $U("Artanis"));
    EUDEndIf()
    f_wwrite_epd(EPD(a) + 0x50 // 4, 0, EncodeUnit("Artanis"))
    # (Line 25) if (u.orderUnitType == py_str("Artanis")) ret += 32;
    if EUDIf()(_ATTC(u, 'orderUnitType') == str("Artanis")):
        ret.__iadd__(32)
        # (Line 28) ret += 64;
    EUDEndIf()
    ret.__iadd__(64)
    # (Line 29) u.cgive(P2);
    u.cgive(P2)
    # (Line 30) if (u.owner == P2) ret += 128;
    if EUDIf()(_ATTC(u, 'owner') == P2):
        ret.__iadd__(128)
        # (Line 32) u.die();
    EUDEndIf()
    u.die()
    # (Line 33) if (a[0x4C/4] == 0x12340001) ret += 256;
    if EUDIf()(_ARRC(a, 0x4C // 4) == 0x12340001):
        ret.__iadd__(256)
        # (Line 34) if (u.is_dying()) ret += 512;
    EUDEndIf()
    if EUDIf()(u.is_dying()):
        ret.__iadd__(512)
        # (Line 35) if (!u.are_buildq_empty()) ret += 1024;
    EUDEndIf()
    if EUDIf()(u.are_buildq_empty(), neg=True):
        ret.__iadd__(1024)
        # (Line 36) if (u.check_buildq(EUDVariable(0x11))) ret += 2048;
    EUDEndIf()
    if EUDIf()(u.check_buildq(EUDVariable(0x11))):
        ret.__iadd__(2048)
        # (Line 38) if (u.check_buildq("Terran Medic")) ret += 4096;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Terran Medic")):
        ret.__iadd__(4096)
        # (Line 39) if (u.check_buildq(EUDVariable(0x33))) ret += 8192;
    EUDEndIf()
    if EUDIf()(u.check_buildq(EUDVariable(0x33))):
        ret.__iadd__(8192)
        # (Line 40) if (u.check_buildq("Protoss Archon")) ret += 16384;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Protoss Archon")):
        ret.__iadd__(16384)
        # (Line 41) if (u.check_buildq("Protoss Scarab")) ret += 32768;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Protoss Scarab")):
        ret.__iadd__(32768)
        # (Line 43) u.reset_buildq();
    EUDEndIf()
    u.reset_buildq()
    # (Line 44) if (u.are_buildq_empty()) ret += 65536;
    if EUDIf()(u.are_buildq_empty()):
        ret.__iadd__(65536)
        # (Line 45) var d = u.movementFlags;
    EUDEndIf()
    d = _LVAR([u.movementFlags])
    # (Line 46) if (d == 0xF8) ret += 1 << 17;
    if EUDIf()(d == 0xF8):
        ret.__iadd__(_LSH(1,17))
        # (Line 47) u.movementFlags += 1;
    EUDEndIf()
    _ATTW(u, 'movementFlags').__iadd__(1)
    # (Line 48) if (u.movementFlags == 0xF9) ret += 1 << 18;
    if EUDIf()(_ATTC(u, 'movementFlags') == 0xF9):
        ret.__iadd__(_LSH(1,18))
        # (Line 49) return ret;
    EUDEndIf()
    EUDReturn(ret)
    # (Line 50) }
    # (Line 51) function test_cunit2() {

@EUDFunc
def f_test_cunit2():
    # (Line 52) const u = CUnit(EUDVariable(EPD(0x59CCA8 + 336)));
    u = CUnit(EUDVariable(EPD(0x59CCA8 + 336)))
    # (Line 53) var ret = 0;
    ret = _LVAR([0])
    # (Line 55) u.orderQueueCount = 123;
    _ATTW(u, 'orderQueueCount') << (123)
    # (Line 56) if (u.orderQueueCount == 123) ret += 1;
    if EUDIf()(_ATTC(u, 'orderQueueCount') == 123):
        ret.__iadd__(1)
        # (Line 57) u.orderQueueCount = 0;
    EUDEndIf()
    _ATTW(u, 'orderQueueCount') << (0)
    # (Line 58) if (u.orderQueueCount == 0) ret += 2;
    if EUDIf()(_ATTC(u, 'orderQueueCount') == 0):
        ret.__iadd__(2)
        # (Line 60) u.currentDirection1 = 234;
    EUDEndIf()
    _ATTW(u, 'currentDirection1') << (234)
    # (Line 61) if (u.currentDirection1 == 234) ret += 4;
    if EUDIf()(_ATTC(u, 'currentDirection1') == 234):
        ret.__iadd__(4)
        # (Line 62) u.currentDirection1 = 0;
    EUDEndIf()
    _ATTW(u, 'currentDirection1') << (0)
    # (Line 63) if (u.currentDirection1 == 0) ret += 8;
    if EUDIf()(_ATTC(u, 'currentDirection1') == 0):
        ret.__iadd__(8)
        # (Line 65) u.turnRadius = 34;
    EUDEndIf()
    _ATTW(u, 'turnRadius') << (34)
    # (Line 66) if (u.turnRadius == 34) ret += 16;
    if EUDIf()(_ATTC(u, 'turnRadius') == 34):
        ret.__iadd__(16)
        # (Line 67) u.turnRadius = 0;
    EUDEndIf()
    _ATTW(u, 'turnRadius') << (0)
    # (Line 68) if (u.turnRadius == 0) ret += 32;
    if EUDIf()(_ATTC(u, 'turnRadius') == 0):
        ret.__iadd__(32)
        # (Line 70) u.velocityDirection1 = 45;
    EUDEndIf()
    _ATTW(u, 'velocityDirection1') << (45)
    # (Line 71) if (u.velocityDirection1 == 45) ret += 64;
    if EUDIf()(_ATTC(u, 'velocityDirection1') == 45):
        ret.__iadd__(64)
        # (Line 72) u.velocityDirection1 = 0;
    EUDEndIf()
    _ATTW(u, 'velocityDirection1') << (0)
    # (Line 73) if (u.velocityDirection1 == 0) ret += 128;
    if EUDIf()(_ATTC(u, 'velocityDirection1') == 0):
        ret.__iadd__(128)
        # (Line 75) u.energy = 567;
    EUDEndIf()
    _ATTW(u, 'energy') << (567)
    # (Line 76) if (u.energy == 567) ret += 256;
    if EUDIf()(_ATTC(u, 'energy') == 567):
        ret.__iadd__(256)
        # (Line 77) u.energy = 0;
    EUDEndIf()
    _ATTW(u, 'energy') << (0)
    # (Line 78) if (u.energy == 0) ret += 512;
    if EUDIf()(_ATTC(u, 'energy') == 0):
        ret.__iadd__(512)
        # (Line 80) u.acceleration = 678;
    EUDEndIf()
    _ATTW(u, 'acceleration') << (678)
    # (Line 81) if (u.acceleration == 678) ret += 1024;
    if EUDIf()(_ATTC(u, 'acceleration') == 678):
        ret.__iadd__(1024)
        # (Line 82) u.acceleration = 0;
    EUDEndIf()
    _ATTW(u, 'acceleration') << (0)
    # (Line 83) if (u.acceleration == 0) ret += 2048;
    if EUDIf()(_ATTC(u, 'acceleration') == 0):
        ret.__iadd__(2048)
        # (Line 85) u.remove();
    EUDEndIf()
    u.remove()
    # (Line 86) if (u.order == 0 && u.userActionFlags & 4) ret += 4096;
    if EUDIf()(EUDSCAnd()(_ATTC(u, 'order') == 0)(u.userActionFlags & 4)()):
        ret.__iadd__(4096)
        # (Line 88) return ret;
    EUDEndIf()
    EUDReturn(ret)
    # (Line 89) }
