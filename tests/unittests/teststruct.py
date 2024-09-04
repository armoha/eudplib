from helper import *


# Basic struct test
class TestStruct(EUDStruct):
    _fields_ = ["x", "y", "z"]

    @EUDMethod
    def setX(self, x):
        self.x = x

    @EUDTypedMethod([selftype])
    def add(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self


@TestInstance
def test_struct():
    a = TestStruct()
    a.x = 5
    a.y = 7

    b = TestStruct.cast(a)
    c = TestStruct.cast(b)
    d = TestStruct.cast(c)

    b.z = 8
    c.x = 3

    test_assert("EUDStruct can be converted to a condition", a)

    test_equality(
        "EUDStruct indirect access test",
        [a.x, b.x, c.x, d.x, a.y, b.y, c.y, d.y, a.z, b.z, c.z, d.z],
        [3, 3, 3, 3, 7, 7, 7, 7, 8, 8, 8, 8],
    )

    d = a.copy()
    a.add(d)
    test_equality(
        "EUDTypedMethod test", [a.x, a.y, a.z, d.x, d.y, d.z], [6, 14, 16, 3, 7, 8]
    )

    e = EUDVariable()
    e << a
    TestStruct.cast(e).setX(1)
    test_equality("EUDStruct method via EUDVariable", a.x, 1)

    # https://github.com/phu54321/euddraft/issues/8
    # Accessing to unknown fields should trigger an error.
    with expect_eperror():
        a.q = 1


# Nested struct test


class Coord(EUDStruct):
    _fields_ = ["x", "y"]


class Triangle(EUDStruct):
    _fields_ = [("p", Coord * 5), "q"]


@TestInstance
def test_nested_struct():
    a = Triangle()
    a.p = (Coord * 5)()
    for i in range(5):
        a.p[i] = Coord()

    a.p[0].x = 1
    a.p[1].y = 2
    a.p[1].y += 2
    a.q = 3

    test_assert(
        "Nested EUDStruct test",
        [a.p[0].x == 1, a.p[0].y == 0, a.p[1].y == 4, a.q == 3],
    )

    b = a.copy()
    b.p[0].x = 5
    b.q = 2
    test_equality(
        "Shallow EUDStruct copy test",
        [a.p[0].x, b.p[0].x, b.p[0].y, b.p[1].y, a.q, b.q],
        [5, 5, 0, 4, 3, 2],
    )

    p5x5 = (Coord * 5 * 5)()
    for i in range(5):
        p5x5[i] = (Coord * 5)()
        for j in range(5):
            p5x5[i][j] = Coord()

    p5x5[0][0].x = 1
    p5x5[0][0].y = 2
    p5x5[1][0].x = 3
    p5x5[0][1].y = 4
    p5x5[1][1].x = 5
    p5x5[1][1].y = 6

    test_equality(
        "Nested EUDStructArray test",
        [
            p5x5[0][0].x,
            p5x5[0][0].y,
            p5x5[0][1].x,
            p5x5[0][1].y,
            p5x5[1][0].x,
            p5x5[1][0].y,
            p5x5[1][1].x,
            p5x5[1][1].y,
        ],
        [1, 2, 0, 4, 3, 0, 5, 6],
    )


@TestInstance
def test_invalid_struct():
    with expect_eperror():
        a = TestStruct()
        a << 5


@TestInstance
def test_cast_0_to_struft():
    a = TestStruct.cast(0)
    test_equality("nullptr casting", a, 0)


# Test referencing itself on member decl
class ListClass(EUDStruct):
    _fields_ = [("prev", selftype), ("next", selftype)]


@TestInstance
def test_selftype_member():
    a = ListClass()
    b = ListClass()
    a.prev = a.next = b
    a.prev = b.next = a
