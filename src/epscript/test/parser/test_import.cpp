//
// Created by phu54321 on 2017-12-10.
//

#include "../test_base.hpp"

TEST_CASE("Import parsing") {
            CHECK(ParseString("test", "import a1;", false) == "import a1\n");
            CHECK(ParseString("test", "import test.a1;", false) == "from test import a1\n");
            CHECK(ParseString("test", "import py_a1;", false) == "import a1\n");
            CHECK(ParseString("test", "import test.py_a1;", false) == "from test import a1\n");
    checkError("import main");
}
