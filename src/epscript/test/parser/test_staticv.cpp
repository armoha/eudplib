//
// Created by phu54321 on 2018-01-23.
//

#include "../test_base.hpp"

TEST_CASE("Static variable") {
    checkBlock("static var x = 0;", "x = EUDVariable(0)\n");
    checkBlock("static var x, y = 0, 1;", "x, y = (EUDVariable(x) for x in (0, 1))\n");
}
