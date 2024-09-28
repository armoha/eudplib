//
// Created by phu54321 on 2018-08-12.
//

#include "../test_base.hpp"

TEST_CASE("Bug case phu54321/euddraft#9") {
    checkBlock("const A = EUDArray(8);\n"
               "A[0]++;",
               "A = EUDArray(8)\n"
               "_ARRW(A, 0).__iadd__(1)");

    checkBlock("const A = EUDArray(8);\n"
               "A[0] += 1;",
               "A = EUDArray(8)\n"
               "_ARRW(A, 0).__iadd__(1)");
}
