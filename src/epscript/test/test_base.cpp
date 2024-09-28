#include "../parser/parser.h"
#include "../utils.h"
#include "catch.hpp"
#include <stdexcept>
#include <algorithm>
#include <string.h>
#include <vector>
#include "test_base.hpp"

std::string unindentString(const std::string& data) {
    std::vector<char> sbuf;
    bool isNewline = true;
    size_t index = 0, dlen = data.size();
    sbuf.reserve(dlen);

    while(index < dlen) {
        if(isNewline && data[index] == ' ') {
            index += 4;  // unindent
            if(index >= dlen) break;
        }
        isNewline = false;

        sbuf.push_back(data[index]);
        if(data[index] == '\n') isNewline = true;
        index++;
    }
    return std::string(sbuf.begin(), sbuf.end());
}
