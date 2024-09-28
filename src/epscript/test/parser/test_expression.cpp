//
// Created by phu54321 on 2018-01-16.
//

#include "../test_base.hpp"


TEST_CASE("Simple arithmetic") {
    checkBlock("return 1 + 2;", "EUDReturn(1 + 2)");
    checkBlock("return 1 * 2;", "EUDReturn(1 * 2)");
    checkBlock("return 1 + 2 * 3;", "EUDReturn(1 + 2 * 3)");
    checkBlock("return dwread_epd(0);", "EUDReturn(f_dwread_epd(0))");
}

TEST_CASE("Logic expressions") {
    checkBlock("return l2v(1 >= 2);", "EUDReturn(_L2V(1 >= 2))");
    checkBlock("return l2v(1 == 2);", "EUDReturn(_L2V(1 == 2))");

    // Negate optimization
    checkBlock("return l2v(1 > 2);", "EUDReturn(_L2V(EUDNot(1 <= 2)))");
    checkBlock("return l2v(1 < 2);", "EUDReturn(_L2V(EUDNot(1 >= 2)))");
    checkBlock("return l2v(1 != 2);", "EUDReturn(_L2V(EUDNot(1 == 2)))");

    // Double inverse get optimized
    checkBlock("return l2v(!!(1 == 2));", "EUDReturn(_L2V((1 == 2)))");
    checkBlock("return l2v(!(1 != 2));", "EUDReturn(_L2V((1 == 2)))");
}
