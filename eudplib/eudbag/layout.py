from . import writebuf as wb

# fmt: off
# See https://github.com/armoha/euddraft/discussions/60
_overlap_distance = (
      20,
      72,  132,  212,  228,  260,  260,  292,  292,
     616,  648,  680,  708,  740,  772,  812,  844,
     876,  908,  940,  972, 1004, 1028, 1060, 1092,
    1124, 1156, 1204, 1236, 1268, 1300, 1332, 1364,
    1396, 1428, 1460, 1492, 1524, 1556, 1588, 1620,
    1652, 1684, 1716, 1748, 1780, 1812, 1844, 1876,
    1908, 1940, 1972, 2004, 2036, 2052, 2084, 2116,
    2148, 2180, 2212, 2244, 2276, 2308, 2340, 2376
)
_write_payload = (
    lambda _buf, _count, _nptr, _val: (_ for _ in ()).throw(Exception('write0')),
     wb.write1,  wb.write2,  wb.write3,  wb.write4,  wb.write5,  wb.write6,  wb.write7,  wb.write8,
     wb.write9, wb.write10, wb.write11, wb.write12, wb.write13, wb.write14, wb.write15, wb.write16,
    wb.write17, wb.write18, wb.write19, wb.write20, wb.write21, wb.write22, wb.write23, wb.write24,
    wb.write25, wb.write26, wb.write27, wb.write28, wb.write29, wb.write30, wb.write31, wb.write32,
    wb.write33, wb.write34, wb.write35, wb.write36, wb.write37, wb.write38, wb.write39, wb.write40,
    wb.write41, wb.write42, wb.write43, wb.write44, wb.write45, wb.write46, wb.write47, wb.write48,
    wb.write49, wb.write50, wb.write51, wb.write52, wb.write53, wb.write54, wb.write55, wb.write56,
    wb.write57, wb.write58, wb.write59, wb.write60, wb.write61, wb.write62, wb.write63, wb.write64,
)
# fmt: on
