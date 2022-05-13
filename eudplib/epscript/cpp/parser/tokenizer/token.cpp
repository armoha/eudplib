//
// Created by phu54321 on 2018-01-26.
//

#include "token.h"

#ifdef MEMORY_DEBUG
#include <set>
#include <map>
#include <iostream>

bool TOKEN_MEMORY_DEBUG = false;

const char *getTokenTypeString(int type)
{
    static std::map<int, const char *> tokTypeMap = {
        {TOKEN_INVALID, "TOKEN_INVALID"},
        {TOKEN_TEMP, "TOKEN_TEMP"},
        {TOKEN_EXPR, "TOKEN_EXPR"},
        {TOKEN_IMPORT, "TOKEN_IMPORT"},
        {TOKEN_AS, "TOKEN_AS"},
        {TOKEN_VAR, "TOKEN_VAR"},
        {TOKEN_CONST, "TOKEN_CONST"},
        {TOKEN_STATIC, "TOKEN_STATIC"},
        {TOKEN_FUNCTION, "TOKEN_FUNCTION"},
        {TOKEN_OBJECT, "TOKEN_OBJECT"},
        {TOKEN_L2V, "TOKEN_L2V"},
        {TOKEN_IF, "TOKEN_IF"},
        {TOKEN_ELSE, "TOKEN_ELSE"},
        {TOKEN_FOR, "TOKEN_FOR"},
        {TOKEN_FOREACH, "TOKEN_FOREACH"},
        {TOKEN_WHILE, "TOKEN_WHILE"},
        {TOKEN_BREAK, "TOKEN_BREAK"},
        {TOKEN_CONTINUE, "TOKEN_CONTINUE"},
        {TOKEN_RETURN, "TOKEN_RETURN"},
        {TOKEN_SWITCHCASE, "TOKEN_SWITCHCASE"},
        {TOKEN_CASE, "TOKEN_CASE"},
        {TOKEN_DEFAULT, "TOKEN_DEFAULT"},
        {TOKEN_NAME, "TOKEN_NAME"},
        {TOKEN_NUMBER, "TOKEN_NUMBER"},
        {TOKEN_STRING, "TOKEN_STRING"},
        {TOKEN_CONDITION, "TOKEN_CONDITION"},
        {TOKEN_ACTION, "TOKEN_ACTION"},
        {TOKEN_ACTION_ALLP, "TOKEN_ACTION_ALLP"},
        {TOKEN_KILLS, "TOKEN_KILLS"},
        {TOKEN_UNITNAME, "TOKEN_UNITNAME"},
        {TOKEN_LOCNAME, "TOKEN_LOCNAME"},
        {TOKEN_MAPSTRING, "TOKEN_MAPSTRING"},
        {TOKEN_SWITCHNAME, "TOKEN_SWITCHNAME"},
        {TOKEN_STATTXTTBL, "TOKEN_STATTXTTBL"},
        {TOKEN_VARRAY, "TOKEN_VARRAY"},
        {TOKEN_LIST, "TOKEN_LIST"},
        {TOKEN_INC, "TOKEN_INC"},
        {TOKEN_DEC, "TOKEN_DEC"},
        {TOKEN_IADD, "TOKEN_IADD"},
        {TOKEN_ISUB, "TOKEN_ISUB"},
        {TOKEN_IMUL, "TOKEN_IMUL"},
        {TOKEN_IDIV, "TOKEN_IDIV"},
        {TOKEN_IMOD, "TOKEN_IMOD"},
        {TOKEN_ILSHIFT, "TOKEN_ILSHIFT"},
        {TOKEN_IRSHIFT, "TOKEN_IRSHIFT"},
        {TOKEN_IBITAND, "TOKEN_IBITAND"},
        {TOKEN_IBITOR, "TOKEN_IBITOR"},
        {TOKEN_IBITXOR, "TOKEN_IBITXOR"},
        {TOKEN_ASSIGN, "TOKEN_ASSIGN"},
        {TOKEN_PLUS, "TOKEN_PLUS"},
        {TOKEN_MINUS, "TOKEN_MINUS"},
        {TOKEN_MULTIPLY, "TOKEN_MULTIPLY"},
        {TOKEN_DIVIDE, "TOKEN_DIVIDE"},
        {TOKEN_MOD, "TOKEN_MOD"},
        {TOKEN_BITLSHIFT, "TOKEN_BITLSHIFT"},
        {TOKEN_BITRSHIFT, "TOKEN_BITRSHIFT"},
        {TOKEN_BITAND, "TOKEN_BITAND"},
        {TOKEN_BITOR, "TOKEN_BITOR"},
        {TOKEN_BITXOR, "TOKEN_BITXOR"},
        {TOKEN_BITNOT, "TOKEN_BITNOT"},
        {TOKEN_LAND, "TOKEN_LAND"},
        {TOKEN_LOR, "TOKEN_LOR"},
        {TOKEN_LNOT, "TOKEN_LNOT"},
        {TOKEN_EQ, "TOKEN_EQ"},
        {TOKEN_LE, "TOKEN_LE"},
        {TOKEN_GE, "TOKEN_GE"},
        {TOKEN_LT, "TOKEN_LT"},
        {TOKEN_GT, "TOKEN_GT"},
        {TOKEN_NE, "TOKEN_NE"},
        {TOKEN_LPAREN, "TOKEN_LPAREN"},
        {TOKEN_RPAREN, "TOKEN_RPAREN"},
        {TOKEN_LBRACKET, "TOKEN_LBRACKET"},
        {TOKEN_RBRACKET, "TOKEN_RBRACKET"},
        {TOKEN_LSQBRACKET, "TOKEN_LSQBRACKET"},
        {TOKEN_RSQBRACKET, "TOKEN_RSQBRACKET"},
        {TOKEN_PERIOD, "TOKEN_PERIOD"},
        {TOKEN_QMARK, "TOKEN_QMARK"},
        {TOKEN_COMMA, "TOKEN_COMMA"},
        {TOKEN_COLON, "TOKEN_COLON"},
        {TOKEN_SEMICOLON, "TOKEN_SEMICOLON"},
    };
    auto it = tokTypeMap.find(type);
    if (it == tokTypeMap.end())
        return "Unknown";
    else
        return it->second;
}

std::set<Token *> allocatedTokenSet;
#define REGISTERTOK                                                          \
    {                                                                        \
        allocatedTokenSet.insert(this);                                      \
        if (TOKEN_MEMORY_DEBUG)                                              \
            printf("[[ allocate(%p): %s\n", this, getTokenTypeString(type)); \
    }

#define UNREGISTERTOK                                                    \
    {                                                                    \
        if (line == 123456)                                              \
            throw std::runtime_error("Double delete");                   \
        auto it = allocatedTokenSet.find(this);                          \
        if (it == allocatedTokenSet.end())                               \
        {                                                                \
            fprintf(stderr, "Unregistered token[%p] deleted!", this);    \
            throw std::runtime_error("Unknown token pointer");           \
        }                                                                \
        else                                                             \
            allocatedTokenSet.erase(it);                                 \
        if (TOKEN_MEMORY_DEBUG)                                          \
            printf("]] free(%p): %s\n", this, getTokenTypeString(type)); \
        line = 123456;                                                   \
    }

void printToken(Token *tok, int indent)
{
    printf("token type:%s(%d), line:%d, data:%s\n", getTokenTypeString(tok->type), tok->type, tok->line, tok->data.c_str());
    for (int i = 0; i < MAX_SUBTOKEN_NUM; i++)
    {
        if (tok->subToken[i])
        {
            printf("%*csubToken[%d]: ", indent * 2 + 2, ' ', i);
            printToken(tok->subToken[i], indent + 1);
        }
    }
}

bool checkLeakedTokens()
{
    if (allocatedTokenSet.empty())
        return true;

    fprintf(stderr, "Leaked tokens: %lu\n", allocatedTokenSet.size());
    for (const auto &tok : allocatedTokenSet)
    {
        printf("  ");
        printToken(tok, 1);
    }
    allocatedTokenSet.clear();

    return false;
}

void clearLeakedTokens()
{
    allocatedTokenSet.clear();
}

#else
#define REGISTERTOK
#define UNREGISTERTOK
bool checkLeakedTokens() { return true; }

#endif

Token::Token(const std::string &data, int line)
    : type(TOKEN_TEMP), data(data), line(line), subToken{
                                                    nullptr,
                                                }
{
    REGISTERTOK;
}
Token::Token(TokenType type, int line)
    : type(type), line(line), subToken{
                                  nullptr,
                              }
{
    REGISTERTOK;
}
Token::Token(TokenType type, const std::string &data, int line)
    : type(type), data(data), line(line), subToken{
                                              nullptr,
                                          }
{
    REGISTERTOK;
}
Token::~Token()
{
    UNREGISTERTOK;
    for (Token *st : subToken)
        delete st;
}
