//
// Created by phu54321 on 2018-01-16.
//

#include "test_base.hpp"

TEST_CASE("test tool test") {
            CHECK(unindentString("    asdf\n    zxcv\n") == "asdf\nzxcv\n");
    checkBlock("", "pass\n");
}

TEST_CASE("Error handling") {
    // Plain expression cannot appear in program-level
    checkError("2;");
}