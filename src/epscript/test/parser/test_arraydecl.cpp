//
// Created by phu54321 on 2017-12-10.
//

#include "../test_base.hpp"

extern bool PARSER_DEBUG;

TEST_CASE("EUDArray declaration using square brackets") {
    check_string(
            "const a = [1, 2, 3];",
            "a = _CGFW(lambda: [_ARR(FlattenList([1, 2, 3]))], 1)[0]"
    );

    check_string(
            "const a = [1, 2, 3, ];",
            "a = _CGFW(lambda: [_ARR(FlattenList([1, 2, 3]))], 1)[0]"
    );
}
