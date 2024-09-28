//
// Created by phu54321 on 2017-12-10.
//

#include "../test_base.hpp"

TEST_CASE("Control block parsing") {
    SECTION("Once") {
        checkBlock(
                "once { const A = 1; }",

                "if EUDExecuteOnce()():\n"
                        "    A = 1\n"
                        "EUDEndExecuteOnce()\n"
        );
    }

    // Logical operator precedence
    SECTION("If") {
        checkBlock(
                "if(1 == 2 || 2 + 3 == 5 && 7 == 8) return 3;",

                "if EUDIf()(EUDSCOr()(1 == 2)(EUDSCAnd()(2 + 3 == 5)(7 == 8)())()):\n"
                        "    EUDReturn(3)\n"
                        "EUDEndIf()\n"
        );

        // If, ElseIf, Else
        checkBlock(
                "if(1 == 2) return 3;\n"
                        "else if(4 == 5) return 6;\n"
                        "else {\n"
                        "    return 7;\n"
                        "}",

                "if EUDIf()(1 == 2):\n"
                        "    EUDReturn(3)\n"
                        "if EUDElseIf()(4 == 5):\n"
                        "    EUDReturn(6)\n"
                        "if EUDElse()():\n"
                        "    EUDReturn(7)\n"
                        "EUDEndIf()\n"
        );
    }

    SECTION("While") {
        // While
        checkBlock(
                "while(1 == 2) continue;",

                "if EUDWhile()(1 == 2):\n"
                        "    EUDContinue()\n"
                        "EUDEndWhile()\n"
        );
    }

    SECTION("Foreach") {
        // forEach
        check_string(
                "function x() {\n"
                        "    const A, B = 1, 1;\n"
                        "    foreach (x : A) {\n"
                        "    }\n"
                        "\n"
                        "    var x;  // Check non-duplicate variable\n"
                        "\n"
                        "    foreach (x, y : B) {\n"
                        "        SetDeaths(x, SetTo, y, 0);\n"
                        "    }\n"
                        "}",

                "@EUDFunc\n"
                        "def f_x():\n"
                        "    A, B = List2Assignable([1, 1])\n"
                        "    for x in A:\n"
                        "        pass\n"
                        "\n"
                        "    x = EUDVariable()\n"
                        "    for x_1, y in B:\n"
                        "        DoActions(SetDeaths(x_1, SetTo, y, 0))"

        );
    }
}
