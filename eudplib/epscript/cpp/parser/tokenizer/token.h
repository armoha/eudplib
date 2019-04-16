//
// Created by phu54321 on 2018-01-26.
//

#pragma once

#ifndef EPSCRIPT_TOKEN_H
#define EPSCRIPT_TOKEN_H

#include <string>

enum TokenType {
    // Internally used by parser
    TOKEN_INVALID = -3,
    TOKEN_TEMP = -2,
    TOKEN_EXPR = -1,

    // Keywords
    TOKEN_IMPORT,
    TOKEN_AS,
    TOKEN_VAR,
    TOKEN_CONST,
    TOKEN_STATIC,
    TOKEN_FUNCTION,
    TOKEN_OBJECT,
    TOKEN_L2V,
    TOKEN_ONCE,
    TOKEN_IF,
    TOKEN_ELSE,
    TOKEN_FOR,
    TOKEN_FOREACH,
    TOKEN_WHILE,
    TOKEN_BREAK,
    TOKEN_CONTINUE,
    TOKEN_RETURN,
    TOKEN_SWITCHCASE,
    TOKEN_CASE,
    TOKEN_DEFAULT,

    // Identifiers
    TOKEN_NAME,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_CONDITION,
    TOKEN_ACTION,
    TOKEN_KILLS,

    TOKEN_UNITNAME,
    TOKEN_LOCNAME,
    TOKEN_MAPSTRING,
    TOKEN_SWITCHNAME,

    TOKEN_VARRAY,
    TOKEN_LIST,

    // Operators
    TOKEN_INC,
    TOKEN_DEC,
    TOKEN_IADD,
    TOKEN_ISUB,
    TOKEN_IMUL,
    TOKEN_IDIV,
    TOKEN_IMOD,
    TOKEN_ILSHIFT,
    TOKEN_IRSHIFT,
    TOKEN_IBITAND,
    TOKEN_IBITOR,
    TOKEN_IBITXOR,
    TOKEN_ASSIGN,

    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_MULTIPLY,
    TOKEN_DIVIDE,
    TOKEN_MOD,
    TOKEN_BITLSHIFT,
    TOKEN_BITRSHIFT,
    TOKEN_BITAND,
    TOKEN_BITOR,
    TOKEN_BITXOR,
    TOKEN_BITNOT,
    TOKEN_LAND,
    TOKEN_LOR,
    TOKEN_LNOT,
    TOKEN_EQ,
    TOKEN_LE,
    TOKEN_GE,
    TOKEN_LT,
    TOKEN_GT,
    TOKEN_NE,

    // Other tokens
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_LBRACKET,
    TOKEN_RBRACKET,
    TOKEN_LSQBRACKET,
    TOKEN_RSQBRACKET,
    TOKEN_PERIOD,
    TOKEN_QMARK,
    TOKEN_COMMA,
    TOKEN_COLON,
    TOKEN_SEMICOLON,
};

const int MAX_SUBTOKEN_NUM = 5;

#ifdef MEMORY_DEBUG
bool checkLeakedTokens();
void clearLeakedTokens();
#endif

struct Token {
    Token(const std::string& data, int line);
    Token(TokenType type, int line);
    Token(TokenType type, const std::string& data, int line);
    ~Token();

    int type;
    std::string data;
    int line;
    Token* subToken[MAX_SUBTOKEN_NUM];
};

#endif //EPSCRIPT_TOKEN_H
