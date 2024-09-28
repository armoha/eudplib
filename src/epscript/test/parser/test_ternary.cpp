//
// Created by phu54321 on 2018-01-08.
//

#include "../test_base.hpp"

TEST_CASE("Ternary operator") {
    checkBlock("return 1 == 1 ? 2 : 3;", "EUDReturn(EUDTernary(1 == 1)(2)(3))\n");

    // Operator precedence
    // This really seems odd, but ternary
    checkBlock("return 1 + (1 == 1) ? 2 : 3;", "EUDReturn(EUDTernary(1 + (1 == 1))(2)(3))\n");
}
