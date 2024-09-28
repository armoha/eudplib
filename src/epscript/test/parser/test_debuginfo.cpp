//
// Created by phu54321 on 2018-01-22.
//

#include "../test_base.hpp"

TEST_CASE("Debug info") {
    MAP_DEBUG = true;

    SECTION("Untyped function") {
        check_string(
                "function x(l) {\n"
                        "\n}",
                "@EUDTracedFunc\n"
                        "def f_x(l):\n"
                        "    pass"
        );
    }

    SECTION("Statements") {
        SECTION("Function call") {
            checkBlock(
                    "dwread_epd(0);",
                    "EUDTraceLog(1)\n"
                            "f_dwread_epd(0)"
            );
        }

        SECTION("Constant declaration") {
            checkBlock(
                    "const A = 1;",
                    "EUDTraceLog(1)\n"
                            "A = 1"
            );
        }
        SECTION("Variable declaration") {
            checkBlock(
                    "var A;",
                    "A = EUDVariable()"  // Pure variable declaration is not traced.
            );

            checkBlock(
                    "static var A = 1;",
                    "A = EUDVariable(1)"  // static variable declaration is not traced.
            );

            checkBlock(  // Variable declaration with assignments.
                    "var A = 1;",
                    "EUDTraceLog(1)\n"
                            "A = EUDVariable()\n"
                            "A << (1)\n"
            );
        }

        SECTION("Assignments") {
            checkBlock(
                "var x, y;\n"
                        "x = 1;\n"
                        "x, y = 1 ,2;\n"
                        "++x;\n"
                        "x++;\n"
                        "--x;\n"
                        "x--;\n"
                        "x += 1;\n"
                        "x -= 2;\n"
                        "x *= 3;\n"
                        "x /= 4;\n"
                        "x %= 5;\n"
                        "x <<= 6;\n"
                        "x >>= 7;\n"
                        "x &= 8;\n"
                        "x ^= 9;\n"
                        "x |= 10;\n",
                "x, y = EUDCreateVariables(2)\n"
                        "EUDTraceLog(2)\n"
                        "x << (1)\n"
                        "EUDTraceLog(3)\n"
                        "_SV([x, y], [1, 2])\n"
                        "EUDTraceLog(4)\n"
                        "x.__iadd__(1)\n"
                        "EUDTraceLog(5)\n"
                        "x.__iadd__(1)\n"
                        "EUDTraceLog(6)\n"
                        "x.__isub__(1)\n"
                        "EUDTraceLog(7)\n"
                        "x.__isub__(1)\n"
                        "EUDTraceLog(8)\n"
                        "x.__iadd__(1)\n"
                        "EUDTraceLog(9)\n"
                        "x.__isub__(2)\n"
                        "EUDTraceLog(10)\n"
                        "x.__imul__(3)\n"
                        "EUDTraceLog(11)\n"
                        "x.__ifloordiv__(4)\n"
                        "EUDTraceLog(12)\n"
                        "x.__imod__(5)\n"
                        "EUDTraceLog(13)\n"
                        "x.__ilshift__(6)\n"
                        "EUDTraceLog(14)\n"
                        "x.__irshift__(7)\n"
                        "EUDTraceLog(15)\n"
                        "x.__iand__(8)\n"
                        "EUDTraceLog(16)\n"
                        "x.__ixor__(9)\n"
                        "EUDTraceLog(17)\n"
                        "x.__ior__(10)\n"
            );
        }

        SECTION("actions") {
            checkBlock(
                "DisplayText('hello world!');",
                "EUDTraceLog(1)\n"
                        "DoActions(DisplayText('hello world!'))"
            );
        }

        SECTION("return") {
            checkBlock(
                    "return 0;",
                    "EUDTraceLog(1)\n"
                            "EUDReturn(0)"
            );
        }

    }

    SECTION("Control blocks") {
        SECTION("If") {
            checkBlock(
                    "if(1) {\n"
                            "    DisplayText('a1');\n"
                            "}\n"
                            "else if(2) {\n"
                            "    DisplayText('a2');\n"
                            "}\n"
                            "else {\n"
                            "    DisplayText('a3');\n"
                            "}",

                    "_t1 = EUDIf()\n"
                            "EUDTraceLog(1)\n"
                            "if _t1(1):\n"
                            "    EUDTraceLog(2)\n"
                            "    DoActions(DisplayText('a1'))\n"
                            "_t2 = EUDElseIf()\n"
                            "EUDTraceLog(4)\n"
                            "if _t2(2):\n"
                            "    EUDTraceLog(5)\n"
                            "    DoActions(DisplayText('a2'))\n"
                            "if EUDElse()():\n"
                            "    EUDTraceLog(8)\n"
                            "    DoActions(DisplayText('a3'))\n"
                            "EUDEndIf()\n"
            );
        }

        SECTION("While") {
            checkBlock(
                    "while(1) {\n"
                            "    const x = 1;\n"
                            "}",

                    "_t1 = EUDWhile()\n"
                            "EUDTraceLog(1)\n"
                            "if _t1(1):\n"
                            "    EUDTraceLog(2)\n"
                            "    x = 1\n"
                            "EUDEndWhile()\n"
            );
        }

        SECTION("For") {
            checkBlock(
                    "for(const i = EUDArray() ; i.empty() ; dwread_epd(i)) {}",

                    "EUDTraceLog(1)\n"
                            "i = EUDArray()\n"
                            "_t1 = EUDWhile()\n"
                            "EUDTraceLog(1)\n"
                            "if _t1(i.empty()):\n"
                            "    def _t2():\n"
                            "        EUDTraceLog(1)\n"
                            "        f_dwread_epd(i)\n"
                            "    EUDSetContinuePoint()\n"
                            "    _t2()\n"
                            "EUDEndWhile()\n"
            );
        }

        SECTION("Break, End") {
            checkBlock(
                    "while(1) {\n"
                            "    continue;\n"
                            "    break;\n"
                            "}",

                    "_t1 = EUDWhile()\n"
                            "EUDTraceLog(1)\n"
                            "if _t1(1):\n"
                            "    EUDTraceLog(2)\n"
                            "    EUDContinue()\n"
                            "    EUDTraceLog(3)\n"
                            "    EUDBreak()\n"
                            "EUDEndWhile()\n"
            );
        }


        // Foreach cannot be traced by now... so sad...

    }

    MAP_DEBUG = false;
}
