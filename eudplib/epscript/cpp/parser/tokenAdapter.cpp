//
// Created by 박현우 on 2016. 11. 28..
//

#include "tokenAdapter.h"

int getConvertedType(int type) {
    switch(type) {
        // Keywords
        case TOKEN_IMPORT: return IMPORT;
        case TOKEN_AS: return AS;
        case TOKEN_VAR: return VAR;
        case TOKEN_CONST: return CONST;
        case TOKEN_STATIC: return STATIC;
        case TOKEN_FUNCTION: return FUNCTION;
        case TOKEN_OBJECT: return OBJECT;
        case TOKEN_CLASS: return CLASS;
        case TOKEN_EXTENDS: return EXTENDS;
        case TOKEN_L2V: return L2V;
        case TOKEN_ONCE: return ONCE;
        case TOKEN_IF: return IF;
        case TOKEN_ELSE: return ELSE;
        case TOKEN_FOR: return FOR;
        case TOKEN_FOREACH: return FOREACH;
        case TOKEN_WHILE: return WHILE;
        case TOKEN_BREAK: return BREAK;
        case TOKEN_CONTINUE: return CONTINUE;
        case TOKEN_RETURN: return RETURN;
        case TOKEN_SWITCHCASE: return SWITCHCASE;
        case TOKEN_EPDSWITCH: return EPDSWITCH;
        case TOKEN_CASE: return CASE;
        case TOKEN_DEFAULT: return DEFAULT;

        // Identifiers
        case TOKEN_NAME: return NAME;
        case TOKEN_NUMBER: return NUMBER;
        case TOKEN_STRING: return STRING;
        case TOKEN_CONDITION: return CONDITIONNAME;
        case TOKEN_ACTION: return ACTIONNAME;
        case TOKEN_ACTION_ALLP: return ACTIONALLPNAME;
        case TOKEN_KILLS: return KILLS;

        case TOKEN_UNITNAME: return UNIT;
        case TOKEN_LOCNAME: return LOCATION;
        case TOKEN_MAPSTRING: return MAPSTRING;
        case TOKEN_SWITCHNAME: return SWITCH;
        case TOKEN_STATTXTTBL: return STATTXTTBL;
        
        case TOKEN_VARRAY: return VARRAY;
        case TOKEN_LIST: return LIST;

        // Assign operators
        case TOKEN_ASSIGN: return ASSIGN;
        case TOKEN_INC: return INC;
        case TOKEN_DEC: return DEC;
        case TOKEN_IADD: return IADD;
        case TOKEN_ISUB: return ISUB;
        case TOKEN_IMUL: return IMUL;
        case TOKEN_IDIV: return IDIV;
        case TOKEN_IMOD: return IMOD;
        case TOKEN_ILSHIFT: return ILSH;
        case TOKEN_IRSHIFT: return IRSH;
        case TOKEN_IBITAND: return IBND;
        case TOKEN_IBITOR: return IBOR;
        case TOKEN_IBITXOR: return IBXR;

        // Operators
        case TOKEN_PLUS: return PLUS;
        case TOKEN_MINUS: return MINUS;
        case TOKEN_MULTIPLY: return MULTIPLY;
        case TOKEN_DIVIDE: return DIVIDE;
        case TOKEN_MOD: return MOD;
        case TOKEN_BITLSHIFT: return LSHIFT;
        case TOKEN_BITRSHIFT: return RSHIFT;
        case TOKEN_BITAND: return BITAND;
        case TOKEN_BITOR: return BITOR;
        case TOKEN_BITXOR: return BITXOR;
        case TOKEN_BITNOT: return BITNOT;
        case TOKEN_LAND: return LAND;
        case TOKEN_LOR: return LOR;
        case TOKEN_LNOT: return LNOT;
        case TOKEN_EQ: return EQ;
        case TOKEN_LE: return LE;
        case TOKEN_GE: return GE;
        case TOKEN_LT: return LT;
        case TOKEN_GT: return GT;
        case TOKEN_NE: return NE;

        // Other tokens
        case TOKEN_LPAREN: return LPAREN;
        case TOKEN_RPAREN: return RPAREN;
        case TOKEN_LBRACKET: return LBRACKET;
        case TOKEN_RBRACKET: return RBRACKET;
        case TOKEN_LSQBRACKET: return LSQBRACKET;
        case TOKEN_RSQBRACKET: return RSQBRACKET;
        case TOKEN_PERIOD: return PERIOD;
        case TOKEN_QMARK: return QMARK;
        case TOKEN_COMMA: return COMMA;
        case TOKEN_COLON: return COLON;
        case TOKEN_SEMICOLON: return SEMICOLON;;
        default: return -1;
    }
}
