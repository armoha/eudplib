//
// Created by phu54321 on 2017-12-10.
//

#include "../test_base.hpp"

TEST_CASE("Object definition") {
    SECTION("Empty object definition & initialization") {
        check_string(
                "object X {}; const t = X();",
                "class X(EUDStruct):\n    _fields_ = [\n    ]\n\nt = _CGFW(lambda: [X()], 1)[0]\n"
        );
    }

    SECTION("Member variable") {
        check_string(
                "object X { var x, y; };",
                "class X(EUDStruct):\n"
                        "    _fields_ = [\n"
                        "        'x',\n"
                        "        'y',\n"
                        "    ]\n"
        );
    }

    SECTION("Typed member variable") {
        check_string(
                "object X { var x: EUDArray, y; };",
                "class X(EUDStruct):\n"
                        "    _fields_ = [\n"
                        "        ('x', EUDArray),\n"
                        "        'y',\n"
                        "    ]\n"
        );
    }

    SECTION("Method") {
        check_string(
                "object X { function x() { return 0; } };",
                "class X(EUDStruct):\n"
                        "    @EUDMethod\n"
                        "    def x(this):\n"
                        "        EUDReturn(0)\n"
                        "\n"
                        "    _fields_ = [\n"
                        "    ]\n"
        );
    }

    SECTION("Method & variable mix") {
        check_string(
            "object V2 {\n"
            "    var x;\n"
            "    function length_sq() {\n"
            "        return this.x * this.x + this.y * this.y;\n"
            "    }\n"
            "    var y;\n"
            "};",

            "class V2(EUDStruct):\n"
                    "    @EUDMethod\n"
                    "    def length_sq(this):\n"
                    "        EUDReturn(this.x * this.x + this.y * this.y)\n"
                    "\n"
                    "    _fields_ = [\n"
                    "        'x',\n"
                    "        'y',\n"
                    "    ]"
        );
    }
}

TEST_CASE("Typed methods") {
    SECTION("Typed parameter") {
        check_string(
                "object X { function x(a: EUDArray) { return 0; } };",
                "class X(EUDStruct):\n"
                        "    @EUDTypedMethod([EUDArray])\n"
                        "    def x(this, a):\n"
                        "        EUDReturn(0)\n\n"
                        "    _fields_ = [\n"
                        "    ]\n"
        );

        check_string(
                "object X { function x(a: EUDArray, b) { return 0; } };",
                "class X(EUDStruct):\n"
                        "    @EUDTypedMethod([EUDArray, None])\n"
                        "    def x(this, a, b):\n"
                        "        EUDReturn(0)\n\n"
                        "    _fields_ = [\n"
                        "    ]\n"
        );
    }

    SECTION("Typed return value") {
        check_string(
                "object X { function x(a: EUDArray): EUDArray { return 0; } };",
                "class X(EUDStruct):\n"
                        "    @EUDTypedMethod([EUDArray], [EUDArray])\n"
                        "    def x(this, a):\n"
                        "        EUDReturn(0)\n\n"
                        "    _fields_ = [\n"
                        "    ]\n"
        );

        check_string(
                "object X { function x(): EUDArray { return 0; } };",
                "class X(EUDStruct):\n"
                        "    @EUDTypedMethod([], [EUDArray])\n"
                        "    def x(this):\n"
                        "        EUDReturn(0)\n\n"
                        "    _fields_ = [\n"
                        "    ]\n"
        );
    }
}


TEST_CASE("Using objects") {
    SECTION("Object methods") {
        check_string(
                "function f(A) {\n"
                        "    const B = EUDByteReader();\n"
                        "    B.seekepd(A);\n"
                        "    A = B.k;\n"
                        "    B.k = 1;\n"
                        "    A, B.k = 3;\n"
                        "    B.x.y = 2;"
                        "}",

                "@EUDFunc\n"
                        "def f_f(A):\n"
                        "    B = EUDByteReader()\n"
                        "    B.seekepd(A)\n"
                        "    A << (B.k)\n"
                        "    _ATTW(B, 'k') << (1)\n"
                        "    _SV([A, _ATTW(B, 'k')], [3])\n"
                        "    _ATTW(B.x, 'y') << (2)\n"
        );
    }
}

TEST_CASE("Allocating objects") {
    check_string(
            "object V2{}; const X = V2.alloc();",

            "class V2(EUDStruct):\n"
                    "    _fields_ = [\n"
                    "    ]\n"
                    "\n"
                    "X = _CGFW(lambda: [V2.alloc()], 1)[0]\n"
    );
}
