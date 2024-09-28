//
// Created by 박현우 on 2016. 11. 27..
//

#include "tokenizerImpl.h"
#include "tokChars.h"
#include "../reservedWords/condAct.h"
#include "../reservedWords/constparser.h"
#include <string.h>
#include <assert.h>

TokenizerImpl::TokenizerImpl(const std::string& is)
        : data(is.begin(), is.end()) {
    // Negative -> Positive
    data.push_back(EOF);
    data.push_back(0);
    cursor = data.data();
    line = 1;
}

TokenizerImpl::~TokenizerImpl() {}

////

int TokenizerImpl::getCurrentLine() const {
    return line;
}

std::string TokenizerImpl::getCurrentLineString() const {
    const char *lineStart = cursor - 1, *lineEnd = cursor;
    while(lineStart > data.data() && *lineStart != '\n') lineStart--;
    if(*lineStart == '\n') lineStart++;
    while(*lineEnd != EOF && *lineEnd != '\n') lineEnd++;
    return std::string(lineStart, lineEnd - lineStart);
}

Token* TokenizerImpl::TK(TokenType type) {
    return new Token(type, line);
}

Token* TokenizerImpl::TK(TokenType type, const std::string& str) {
    return new Token(type, str, line);
}

#define MATCHSTR(s, tokenType) \
    if(strncmp(s, cursor, sizeof(s) - 1) == 0) { \
        cursor += sizeof(s) - 1; \
        return TK(tokenType, s); \
}

static_assert(sizeof("string") == 7, "sizeof string should be strlen(str) + 1");

Token* TokenizerImpl::getToken() {
    do {
        // Skip spaces, including newline
        while (isSpaceOrNewline(*cursor)) {
            // Skipped through newline.
            if (*cursor == '\n') {
                line++;
                cursor++;
            } else cursor++;
        }

        // Skip line comments
        if (cursor[0] == '/' && cursor[1] == '/') {
            while(*cursor != '\n') cursor++;
            continue;
        }

        // Skip multiline comments
        else if (cursor[0] == '/' && cursor[1] == '*') {
            cursor += 2;
            while(*cursor != EOF && !(cursor[0] == '*' && cursor[1] == '/')) {
                if(*cursor == '\n') line++;
                cursor++;
            }
            if(*cursor != EOF) cursor += 2;
            continue;
        }
        break;
    } while(true);

    // EOF check
    assert(cursor <= data.data() + data.size() - 2);
    if(cursor >= data.data() + data.size() - 2) {
        return nullptr;  // EOF
    }

    // String
    char stringOpener = '\0';
    bool isBinaryString = false;
    if(*cursor == '\"' || *cursor == '\'') {
        stringOpener = *cursor;
        cursor++;
    }
    else if(cursor[0] == 'b' && (cursor[1] == '\"' || cursor[1] == '\'')) {
        stringOpener = cursor[1];
        isBinaryString = true;
        cursor += 2;
    }
    if(stringOpener) {
        std::vector<char> buffer;  // String to hold escaped content.
        buffer.reserve(200);

        if(isBinaryString) buffer.push_back('b');

        buffer.push_back(stringOpener);

        while(*cursor != stringOpener) {
            if(*cursor == '\n' || *cursor == EOF) { // Line end during string - Invalid token
                // We don't skip newlines We need to count lines using them.
                // Return invalid token message
                return TK(TOKEN_INVALID);
            }
            else if(*cursor == '\\') {  // Escape character
                cursor++;
                if(*cursor == '\n') {
                    cursor++;
                    line++;
                }

                    // No special procesing is required. Python will take care of that.
                else {
                    buffer.push_back('\\');
                    buffer.push_back(*cursor);
                    cursor++;
                }
            }
            else {
                buffer.push_back(*cursor);
                cursor++;
            }
        }
        cursor++;
        buffer.push_back(stringOpener);
        return TK(TOKEN_STRING, std::string(buffer.data(), buffer.size()));
    }

    // Identifiers
    if(isNameLeadChar(*cursor)) {
        const char* idfStart = cursor;
        while(isNameBodyChar(*(++cursor)));
        std::string identifier(idfStart, cursor - idfStart);

        if(identifier == "$U") return TK(TOKEN_UNITNAME);
        if(identifier == "$L") return TK(TOKEN_LOCNAME);
        if(identifier == "$S") return TK(TOKEN_SWITCHNAME);
        if(identifier == "$T") return TK(TOKEN_MAPSTRING);
        if(identifier == "$B") return TK(TOKEN_STATTXTTBL);

        if(identifier == "VArray") return TK(TOKEN_VARRAY);
        if(identifier == "list") return TK(TOKEN_LIST);

        if(identifier == "import") return TK(TOKEN_IMPORT);
        if(identifier == "as") return TK(TOKEN_AS);
        if(identifier == "var") return TK(TOKEN_VAR);
        if(identifier == "const") return TK(TOKEN_CONST);
        if(identifier == "static") return TK(TOKEN_STATIC);
        if(identifier == "function") return TK(TOKEN_FUNCTION);
        if(identifier == "object") return TK(TOKEN_OBJECT);
        if(identifier == "extends") return TK(TOKEN_EXTENDS);
        if(identifier == "l2v") return TK(TOKEN_L2V);
        if(identifier == "once") return TK(TOKEN_ONCE);
        if(identifier == "if") return TK(TOKEN_IF);
        if(identifier == "else") return TK(TOKEN_ELSE);
        if(identifier == "for") return TK(TOKEN_FOR);
        if(identifier == "foreach") return TK(TOKEN_FOREACH);
        if(identifier == "while") return TK(TOKEN_WHILE);
        if(identifier == "break") return TK(TOKEN_BREAK);
        if(identifier == "continue") return TK(TOKEN_CONTINUE);
        if(identifier == "return") return TK(TOKEN_RETURN);
        if(identifier == "switch") return TK(TOKEN_SWITCHCASE);
        if(identifier == "epdswitch") return TK(TOKEN_EPDSWITCH);
        if(identifier == "case") return TK(TOKEN_CASE);
        if(identifier == "default") return TK(TOKEN_DEFAULT);

        if(identifier == "Kills") return TK(TOKEN_KILLS, identifier);

        if(isConditionName(identifier)) return TK(TOKEN_CONDITION, identifier);
        if(isActionName(identifier)) return TK(TOKEN_ACTION, identifier);
        if(isActionAllpName(identifier)) return TK(TOKEN_ACTION_ALLP, identifier);
        int c;
        if((c = parseConstantName(identifier)) != -1) return TK(TOKEN_NUMBER, std::to_string(c));

        return TK(TOKEN_NAME, identifier);
    }


    // Numbers
    if('0' <= *cursor && *cursor <= '9') {
        const char* numberStart = cursor;
        // Hexadecimal number
        if((
                (cursor[1] == 'x' || cursor[1] == 'X') &&
                isxdigit(cursor[2]))) {
            cursor += 2;
            int num = 0, chnum = 0;
            while((chnum = getXDigitInt(*cursor)) != -1) {
                num = (num << 4) | chnum;
                cursor++;
            }
        }
        // Binary number
        else if((cursor[1] == 'b' && (cursor[2] == '0' || cursor[2] == '1'))) {
            cursor += 2;
            int num = 0;
            while('0' <= *cursor && *cursor <= '1') {
                num = num * 2 + (*cursor - '0');
                cursor++;
            }
        }
        // Decimal number
        else {
            int num = 0;
            while('0' <= *cursor && *cursor <= '9') {
                num = num * 10 + (*cursor - '0');
                cursor++;
            }
        }
        return TK(TOKEN_NUMBER, std::string(numberStart, cursor - numberStart));
    }

    // Inplace operators
    MATCHSTR("++", TOKEN_INC);
    MATCHSTR("--", TOKEN_DEC);
    MATCHSTR("+=", TOKEN_IADD);
    MATCHSTR("-=", TOKEN_ISUB);
    MATCHSTR("*=", TOKEN_IMUL);
    MATCHSTR("/=", TOKEN_IDIV);
    MATCHSTR("%=", TOKEN_IMOD);
    MATCHSTR("<<=", TOKEN_ILSHIFT);
    MATCHSTR(">>=", TOKEN_IRSHIFT);
    MATCHSTR("&=", TOKEN_IBITAND);
    MATCHSTR("^=", TOKEN_IBITXOR);
    MATCHSTR("|=", TOKEN_IBITOR);

    // Operators
    MATCHSTR("&&", TOKEN_LAND);
    MATCHSTR("||", TOKEN_LOR);

    MATCHSTR("<<", TOKEN_BITLSHIFT);
    MATCHSTR(">>", TOKEN_BITRSHIFT);
    MATCHSTR("~", TOKEN_BITNOT);
    MATCHSTR("&", TOKEN_BITAND);  // After TOKEN_LAND
    MATCHSTR("|", TOKEN_BITOR);  // After TOKEN_LOR
    MATCHSTR("^", TOKEN_BITXOR);

    MATCHSTR("==", TOKEN_EQ);
    MATCHSTR("<=", TOKEN_LE);
    MATCHSTR(">=", TOKEN_GE);
    MATCHSTR("<", TOKEN_LT);  // After TOKEN_BITLSHIFT
    MATCHSTR(">", TOKEN_GT);  // After TOKEN_BITRSHIFT
    MATCHSTR("!=", TOKEN_NE);  // After TOKEN_LNOT

    MATCHSTR("!", TOKEN_LNOT);

    MATCHSTR("+", TOKEN_PLUS);
    MATCHSTR("-", TOKEN_MINUS);
    MATCHSTR("*", TOKEN_MULTIPLY);
    MATCHSTR("/", TOKEN_DIVIDE);
    MATCHSTR("%", TOKEN_MOD);

    MATCHSTR("=", TOKEN_ASSIGN);  // After Comparators

    // Special chars
    MATCHSTR("(", TOKEN_LPAREN);
    MATCHSTR(")", TOKEN_RPAREN);
    MATCHSTR("[", TOKEN_LSQBRACKET);
    MATCHSTR("]", TOKEN_RSQBRACKET);
    MATCHSTR("{", TOKEN_LBRACKET);
    MATCHSTR("}", TOKEN_RBRACKET);
    MATCHSTR(".", TOKEN_PERIOD);
    MATCHSTR("?", TOKEN_QMARK);
    MATCHSTR(",", TOKEN_COMMA);
    MATCHSTR(":", TOKEN_COLON);
    MATCHSTR(";", TOKEN_SEMICOLON);

    printf("Unknown token %c(%d)\n", *cursor, *cursor);
    cursor++;  // Skip invalid token
    return TK(TOKEN_INVALID);
}
