// Streambuf

#include <string>
#include <streambuf>
#include <sstream>
#include "pygen.h"

class PyGeneratorBuf : public std::streambuf
{
public:
    PyGeneratorBuf() : currentIndent(0), lineStart(false), justIndented(false), justUnindented(false) {}
    ~PyGeneratorBuf() {}

    std::string str() { return os.str(); }
    void indent()
    {
        currentIndent += 4;
        justIndented = true;
        justUnindented = false;
    }
    void unindent(bool issueNewline)
    {
        if (currentIndent == 0)
        {
            throw std::logic_error("Not enough closures");
        }
        else if (justIndented)
        {
            // Indented with no content. Add pass.
            for (int i = 0; i < currentIndent; i++)
            {
                os.put(' ');
            }
            os << "pass\n";
        }
        currentIndent -= 4;

        if (issueNewline && !justUnindented)
            os.put('\n');
        justIndented = false;
        justUnindented = true;
    }

    virtual int overflow(int c)
    {
        if (c == EOF)
            return EOF;

        char ch = static_cast<char>(c);

        // Indent at the start of the line
        if (lineStart)
        {
            // Sequential linebreaks -> don't indent empty line
            if (ch == '\n')
            {
                os.put(ch);
                return ch;
            }

            // Comment line -> Don't count as new line after indenting
            else if (ch == '#')
                ;
            else
                justIndented = false;

            // Indent line
            for (int i = 0; i < currentIndent; i++)
            {
                os.put(' ');
            }
            lineStart = false;
        }
        os.put(ch);

        // Set linestart at the end of the line
        if (ch == '\n')
        {
            lineStart = true;
        }

        justUnindented = false;
        return ch;
    }

private:
    std::ostringstream os;
    int currentIndent;
    bool lineStart;
    bool justIndented;
    bool justUnindented;
};

PyGenerator::PyGenerator()
    : std::ostream(new PyGeneratorBuf)
{
    pbuf = static_cast<PyGeneratorBuf *>(rdbuf());
}

PyGenerator::~PyGenerator()
{
    delete pbuf;
}

std::string PyGenerator::str()
{
    std::string str = pbuf->str();
    if (str.size() > 2)
    {
        if (str[str.size() - 1] == '\n' && str[str.size() - 2] == '\n')
        {
            str = str.substr(0, str.size() - 1);
        }
    }
    return str;
}

void PyGenerator::indent()
{
    pbuf->indent();
}

void PyGenerator::unindent(bool issueNewline)
{
    pbuf->unindent(issueNewline);
}
