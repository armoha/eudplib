//
// Created by phu54321 on 2018-01-16.
//

#include "../test_base.hpp"

TEST_CASE("Function parsing") {
    SECTION("Untyped function") {
        check_string(
                "function x(l) {}",
                "@EUDFunc\n"
                        "def f_x(l):\n"
                        "    pass\n"
        );
    }

    SECTION("Position of return statement") {
        check_string(
                "function x(l) { return 1; }",
                "@EUDFunc\n"
                        "def f_x(l):\n"
                        "    EUDReturn(1)\n"
        );
        check_string(
                "function x(l) { return 1; var a;}",
                "@EUDFunc\n"
                        "def f_x(l):\n"
                        "    EUDReturn(1)\n"
                        "    a = EUDVariable()"
        );
    }

    SECTION("Typed Function parsing") {
        check_string(
                "function x(a: EUDArray) {}",
                "@EUDTypedFunc([EUDArray])\n"
                        "def f_x(a):\n"
                        "    pass\n"
        );
    }

    SECTION("Typed returned function parsing") {
        SECTION("Only parameter types") {
            check_string(
                    "function x(a: EUDArray) {}",
                    "@EUDTypedFunc([EUDArray])\n"
                            "def f_x(a):\n"
                            "    pass\n"
            );
        }

        SECTION("Only return types") {
            check_string(
                    "function x(a): EUDArray {}",
                    "@EUDTypedFunc([None], [EUDArray])\n"
                            "def f_x(a):\n"
                            "    pass\n"
            );
        }


        SECTION("Parameter and return types") {
            check_string(
                    "function x(a: EUDArray): EUDArray {}",
                    "@EUDTypedFunc([EUDArray], [EUDArray])\n"
                            "def f_x(a):\n"
                            "    pass\n"
            );
        }

        SECTION("Mixed parameter types.") {
            check_string(
                    "function x(a: EUDArray, b, c: EUDByteReader) {}",
                    "@EUDTypedFunc([EUDArray, None, EUDByteReader])\n"
                            "def f_x(a, b, c):\n"
                            "    pass\n"
            );
        }

        SECTION("Multiple return types") {
            check_string(
                    "function x(): None, EUDArray {}",
                    "@EUDTypedFunc([], [None, EUDArray])\n"
                            "def f_x():\n"
                            "    pass\n"
            );
        }
    }
}

