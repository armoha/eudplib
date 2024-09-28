//
// Created by 박현우 on 2016. 11. 26..
//

#ifndef EPSCRIPT_TOKENIZER_H
#define EPSCRIPT_TOKENIZER_H

#include <istream>
#include <vector>
#include <memory>

#include "token.h"

class TokenizerImpl;
class Tokenizer {
public:
    Tokenizer(const std::string& data);
    ~Tokenizer();

    Token* getToken();
    int getCurrentLine() const;
    std::string getCurrentLineString() const;

private:
    TokenizerImpl* _impl;
};

#endif //EPSCRIPT_TOKENIZER_H
