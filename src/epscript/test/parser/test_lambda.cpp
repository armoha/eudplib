//
// Created by phu54321 on 2018-01-21.
//

#include "../test_base.hpp"

TEST_CASE("Basic lambda functions") {
    check_string(
            "function x() {\n"
                    "    const a = function(x) { return x + 1; };\n"
                    "    return a(1);\n"
                    "}",
            "@EUDFunc\n"
                    "def f_x():\n"
                    "    @EUDFunc\n"
                    "    def _lambda1(x):\n"
                    "        EUDReturn(x + 1)\n"
                    "\n"
                    "    a = _lambda1\n"
                    "    EUDReturn(a(1))"
    );
}
