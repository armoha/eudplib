## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.epscript.helper import _RELIMP, _IGVA, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LVAR, _LSH
# (Line 1) function test_cunit() {
@EUDFunc
def f_test_cunit():
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
    # (Line 12) var ret = 0;
    ret = _LVAR([0])
    # (Line 13) if (u.order == 0x56) ret += 1;
    if EUDIf()(_ATTC(u, 'order') == 0x56):
        ret.__iadd__(1)
        # (Line 14) if (u.owner == P8) ret += 2;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'owner') == P8):
        ret.__iadd__(2)
        # (Line 15) if (u.orderState == 0x34) ret += 4;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderState') == 0x34):
        ret.__iadd__(4)
        # (Line 16) if (u.orderSignal == 0x12) ret += 8;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderSignal') == 0x12):
        ret.__iadd__(8)
        # (Line 18) if (u.orderUnitType == 0xCDEF) ret += 16;
    EUDEndIf()
    if EUDIf()(_ATTC(u, 'orderUnitType') == 0xCDEF):
        ret.__iadd__(16)
        # (Line 19) wwrite_epd(EPD(a) + 0x50/4, 0, $U("Artanis"));
    EUDEndIf()
    f_wwrite_epd(EPD(a) + 0x50 // 4, 0, EncodeUnit("Artanis"))
    # (Line 20) if (u.orderUnitType == py_str("Artanis")) ret += 32;
    if EUDIf()(_ATTC(u, 'orderUnitType') == str("Artanis")):
        ret.__iadd__(32)
        # (Line 23) ret += 64;
    EUDEndIf()
    ret.__iadd__(64)
    # (Line 24) u.cgive(P2);
    u.cgive(P2)
    # (Line 25) if (u.owner == P2) ret += 128;
    if EUDIf()(_ATTC(u, 'owner') == P2):
        ret.__iadd__(128)
        # (Line 27) u.die();
    EUDEndIf()
    u.die()
    # (Line 28) if (a[0x4C/4] == 0x12340001) ret += 256;
    if EUDIf()(_ARRC(a, 0x4C // 4) == 0x12340001):
        ret.__iadd__(256)
        # (Line 29) if (u.is_dying()) ret += 512;
    EUDEndIf()
    if EUDIf()(u.is_dying()):
        ret.__iadd__(512)
        # (Line 30) if (!u.are_buildq_empty()) ret += 1024;
    EUDEndIf()
    if EUDIf()(u.are_buildq_empty(), neg=True):
        ret.__iadd__(1024)
        # (Line 31) if (u.check_buildq(EUDVariable(0x11))) ret += 2048;
    EUDEndIf()
    if EUDIf()(u.check_buildq(EUDVariable(0x11))):
        ret.__iadd__(2048)
        # (Line 33) if (u.check_buildq("Terran Medic")) ret += 4096;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Terran Medic")):
        ret.__iadd__(4096)
        # (Line 34) if (u.check_buildq(EUDVariable(0x33))) ret += 8192;
    EUDEndIf()
    if EUDIf()(u.check_buildq(EUDVariable(0x33))):
        ret.__iadd__(8192)
        # (Line 35) if (u.check_buildq("Protoss Archon")) ret += 16384;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Protoss Archon")):
        ret.__iadd__(16384)
        # (Line 36) if (u.check_buildq("Protoss Scarab")) ret += 32768;
    EUDEndIf()
    if EUDIf()(u.check_buildq("Protoss Scarab")):
        ret.__iadd__(32768)
        # (Line 38) u.reset_buildq();
    EUDEndIf()
    u.reset_buildq()
    # (Line 39) if (u.are_buildq_empty()) ret += 65536;
    if EUDIf()(u.are_buildq_empty()):
        ret.__iadd__(65536)
        # (Line 40) return ret;
    EUDEndIf()
    EUDReturn(ret)
    # (Line 41) }
