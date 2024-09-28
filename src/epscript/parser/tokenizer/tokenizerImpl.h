//
// Created by 박현우 on 2016. 11. 27..
//

#ifndef EPSCRIPT_TOKENIZERIMPL_H
#define EPSCRIPT_TOKENIZERIMPL_H

#include "tokenizer.h"

class TokenizerImpl {
public:
    TokenizerImpl(const std::string& data);
    ~TokenizerImpl();
    Token* getToken();
    int getCurrentLine() const;
    std::string getCurrentLineString() const;

private:
    Token* TK(TokenType type);
    Token* TK(TokenType type, const std::string& data);

private:
    std::vector<char> data;
    char* cursor;
    int line;

};

#endif //EPSCRIPT_TOKENIZERIMPL_H
