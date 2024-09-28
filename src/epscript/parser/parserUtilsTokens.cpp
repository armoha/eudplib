#include "parserUtilities.h"
#include "tokenizer/tokenizer.h"
#include <string.h>

extern int currentTokenizingLine;

void checkIsConstant(std::string& objName, int line) {
    // Python function should pass through.
    if(strncmp(objName.c_str(), "py_", 3) == 0) {
        objName = objName.substr(3);
        return;
    }

    if (!closure->getConstant(objName)) {
        if(closure->defConstant(objName)) {
            throw_error(8200, ("Undefined constant " + objName), line);
        }
        else {
            throw_error(553, ("Not a constant : " + objName), line);
        }
    }
}

void checkIsVariable(std::string& objName, int line) {
    // Python function should pass through.
    if(strncmp(objName.c_str(), "py_", 3) == 0) {
        objName = objName.substr(3);
        return;
    }

    if (!closure->getVariable(objName)) {
        if(closure->defVariable(objName)) {
            throw_error(9571, ("Undefined variable " + objName), line);
        }
        else {
            throw_error(7364, ("Not a variable : " + objName), line);
        }
    }
}

void checkIsFunction(std::string& objName, int line) {
    // Python function should pass through.
    if(strncmp(objName.c_str(), "py_", 3) == 0) {
        objName = objName.substr(3);
        return;
    }

    if (!closure->getFunction(objName)) {
        if(closure->defFunction(objName)) {
            throw_error(7041, ("Undefined function " + objName), line);
        }
        else {
            throw_error(3967, ("Not a function : " + objName), line);
        }
    }
}

void checkIsRValue(std::string& objName, int line) {
    if (!closure->getVariable(objName) && !closure->getConstant(objName)) {
        if(closure->defVariable(objName)) {
            throw_error(9571, ("Undefined rvalue " + objName + " : assuming as variable"), line);
        }
        else {
            throw_error(7364, ("Not an rvalue : " + objName), line);
        }
    }
}





////

Token* genEmpty() {
    return new Token(TOKEN_TEMP, currentTokenizingLine);
}


int tmpIndex = 0;
Token* genTemp(Token* lineSrc) {
    static char output[20] = "_t";
    sprintf(output, "_t%d", tmpIndex++);
    return new Token(output, lineSrc->line);
}

Token* mkTokenTemp(Token* a) {
    a->type = TOKEN_TEMP;
    return a;
}

Token* binopConcat(Token* a, const std::string& opstr, Token* b) {
    b->data = a->data + (" " + opstr + " ") + b->data;
    delete a;
    return mkTokenTemp(b);
}

Token* commaConcat(Token* a, Token* b) {
    b->data = a->data + ", " + b->data;
    delete a;
    return b;
}

void shortCircuitCondListGetter(std::ostream& os, const Token* t, TokenType astType) {
    if(t->type == astType) {
        shortCircuitCondListGetter(os, t->subToken[0], astType);
        shortCircuitCondListGetter(os, t->subToken[1], astType);
    }
    else {
        applyNegativeOptimization(os, t);
    }
}

Token* negate(Token* B) {
    Token* A;
    bool isBGrouped = false;
    if (B->type == TOKEN_EXPR) {
        isBGrouped = true;
        do {
            Token* B1 = B->subToken[0];
            B->subToken[0] = nullptr;
            delete B;
            B = B1;
        } while(B->type == TOKEN_EXPR);
    }

    if(B->type == TOKEN_LNOT) {
        A = B->subToken[0];
        B->subToken[0] = nullptr;
        delete B;
    }
    else {
        A = genEmpty();
        A->line = B->line;
        A->type = TOKEN_LNOT;
        A->data = "EUDNot(" + B->data + ")";
        A->subToken[0] = B;
    }

    if (isBGrouped) {
        Token* A1 = genEmpty();
        A1->type = TOKEN_EXPR;
        A1->subToken[0] = A;
        A1->data = "(" + A->data + ")";
        A = A1;
    }
    return A;
}
////
