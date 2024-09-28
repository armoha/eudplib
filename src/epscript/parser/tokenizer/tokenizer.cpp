#include "tokenizer.h"
#include "tokenizerImpl.h"

Tokenizer::Tokenizer(const std::string& is) : _impl(new TokenizerImpl(is)) {}
Tokenizer::~Tokenizer() { delete _impl; }
Token* Tokenizer::getToken() { return _impl->getToken(); }
int Tokenizer::getCurrentLine() const { return _impl->getCurrentLine(); }
std::string Tokenizer::getCurrentLineString() const { return _impl->getCurrentLineString(); }
