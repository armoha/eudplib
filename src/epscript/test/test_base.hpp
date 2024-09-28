//
// Created by phu54321 on 2017-12-10.
//

#pragma once

#include "../parser/parser.h"
#include "../utils.h"
#include "../parser/tokenizer/token.h"
#include "catch.hpp"
#include <stdexcept>
#include <cstring>
#include <vector>

extern bool PARSER_DEBUG, MAP_DEBUG;

std::string unindentString(const std::string& data);
std::string trim(std::string s);  // Declared from parserUtilites.h

#define check_string(in, out) \
    CHECK(trim(ParseString("<test>", in, false)) == trim(out)); \
    CHECK(checkLeakedTokens())

#define checkError(_input) CHECK((ParseString("<test>", _input), getParseErrorNum() > 0));
#define checkBlock(_input, _output) \
    { \
        std::string input(_input), desiredOutput(_output); \
        std::string output = ParseString("<test>", "function testf() {" + input + "}", false); \
        const char *header = (MAP_DEBUG) ? "@EUDTracedFunc\ndef f_testf():\n" : "@EUDFunc\ndef f_testf():\n"; \
        REQUIRE(strncmp(output.c_str(), header, strlen(header)) == 0); \
        output = unindentString(output.substr(strlen(header))); \
        CHECK(trim(output) == trim(desiredOutput)); \
        CHECK(checkLeakedTokens()); \
    }
