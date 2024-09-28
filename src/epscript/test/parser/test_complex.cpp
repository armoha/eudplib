//
// Created by phu54321 on 2017-12-10.
//

#include "../test_base.hpp"

TEST_CASE("Complex parsing: Integration tests") {
    check_string(
            "var a = 1;\n"
                    "const b = 2;\n"
                    "\n"
                    "function x() {\n"
                    "    const A = 1;\n"
                    "    A.B();  // Should not have f_A prefix\n"
                    "    dwread();  // Should have f_ prefix\n"
                    "\n"
                    "    var a = dwread()[[5]];\n"
                    "    a = A[5];\n"
                    "    A[a] = 7;\n"
                    "}",

            "a = EUDCreateVariables(1)\n"
                    "_IGVA([a], lambda: [1])\n"
                    "b = _CGFW(lambda: [2], 1)[0]\n"
                    "@EUDFunc\n"
                    "def f_x():\n"
                    "    A = 1\n"
                    "    A.B()\n"
                    "    f_dwread()\n"
                    "    a_1 = EUDVariable()\n"
                    "    a_1 << (f_dwread()[5])\n"
                    "    a_1 << (A[5])\n"
                    "    _ARRW(A, a_1) << (7)\n"
    );
}
