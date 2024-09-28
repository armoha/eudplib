//
// Created by phu54321 on 2018-01-10.
//

#include "../test_base.hpp"

TEST_CASE("True, False, and None should be accepted") {
    checkBlock("return True;", "EUDReturn(True)\n");
    checkBlock("return true;", "EUDReturn(True)\n");
    checkBlock("return False;", "EUDReturn(False)\n");
    checkBlock("return false;", "EUDReturn(False)\n");
    checkBlock("return None;", "EUDReturn(None)\n");
}
