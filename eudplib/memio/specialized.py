from .. import utils as ut
from .memifgen import f_readgen_cp, f_readgen_epd

# CUnit
f_cunitread_epd = f_readgen_epd(0x3FFFF0, (0x400008, lambda x: x), _check_empty=True)
f_cunitread_cp = f_readgen_cp(0x3FFFF0, (0x400008, lambda x: x), _check_empty=True)
f_cunitepdread_epd = f_readgen_epd(
    0x3FFFF0,
    (0x400008, lambda x: x),
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_cunitepdread_cp = f_readgen_cp(
    0x3FFFF0,
    (0x400008, lambda x: x),
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_epdcunitread_epd = f_readgen_epd(
    0x3FFFF0,
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_epdcunitread_cp = f_readgen_cp(
    0x3FFFF0,
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
# CSprite
f_epdspriteread_epd = f_readgen_epd(
    0x1FFFC, (0x188000 - 0x58A364 // 4, lambda x: x // 4), _check_empty=True
)
f_epdspriteread_cp = f_readgen_cp(
    0x1FFFC, (0x188000 - 0x58A364 // 4, lambda x: x // 4), _check_empty=True
)
f_spriteepdread_epd = f_readgen_epd(
    0x1FFFC,
    (0x620000, lambda x: x),
    (0x188000 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_spriteepdread_cp = f_readgen_cp(
    0x1FFFC,
    (0x620000, lambda x: x),
    (0x188000 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_spriteread_epd = f_readgen_epd(0x1FFFC, (0x620000, lambda x: x), _check_empty=True)
f_spriteread_cp = f_readgen_cp(0x1FFFC, (0x620000, lambda x: x), _check_empty=True)


def _map_xy_mask():
    from ..core.mapdata import GetChkTokenized

    chkt = GetChkTokenized()
    dim = chkt.getsection("DIM")
    x, y = ut.b2i2(dim[0:2]), ut.b2i2(dim[2:4])
    x, y = (x - 1).bit_length(), (y - 1).bit_length()
    x = 2 ** (x + 5) - 1
    y = 2 ** (y + 5) - 1
    return x, y


def _posread_epd():
    f = getattr(_posread_epd, "f", None)
    if f is None:
        f = f_readgen_epd(
            (lambda x, y: x + 65536 * y)(*_map_xy_mask()),
            (0, lambda x: x if x <= 0xFFFF else 0),
            (0, lambda y: y >> 16),
        )
        _posread_epd.f = f
    return f


def f_posread_epd(epd, **kwargs):
    return _posread_epd()(epd, **kwargs)


def f_posread_cp(cpoffset, **kwargs):
    _rf = getattr(f_posread_cp, "_rf", None)
    if _rf is None:
        _rf = f_readgen_cp(
            (lambda x, y: x + 65536 * y)(*_map_xy_mask()),
            (0, lambda x: x if x <= 0xFFFF else 0),
            (0, lambda y: y >> 16),
        )
        f_posread_cp._rf = _rf
    return _rf(cpoffset, **kwargs)


def _mapxread_epd():
    f = getattr(_mapxread_epd, "f", None)
    if f is None:
        f = tuple(
            f_readgen_epd(_map_xy_mask()[0] << shift, (0, lambda x: x >> shift))
            for shift in (0, 16)
        )
        _mapxread_epd.f = f
    return f


def _mapyread_epd():
    f = getattr(_mapyread_epd, "f", None)
    if f is None:
        f = tuple(
            f_readgen_epd(_map_xy_mask()[1] << shift, (0, lambda x: x >> shift))
            for shift in (0, 16)
        )
        _mapyread_epd.f = f
    return f


def _boolread_epd():
    f = getattr(_boolread_epd, "f", None)
    if f is None:
        f = tuple(
            f_readgen_epd(1 << shift, (0, lambda x: 1)) for shift in range(0, 32, 8)
        )
        _boolread_epd.f = f
    return f


def _playerread_epd():
    f = getattr(_playerread_epd, "f", None)
    if f is None:
        f = tuple(
            f_readgen_epd(0xF << shift, (0, lambda x: x >> shift))
            for shift in range(0, 32, 8)
        )
        _playerread_epd.f = f
    return f
