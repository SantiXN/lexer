import os
import re
import sys

from token import Token, Operator, KeyWord


class Lexer:
    IdentifierPattern = r"^[a-zA-Z_][a-zA-Z0-9_]*"
    StringPattern = r"^'(.*?)'"
    NumberPattern = r"^\d+(\.)?(\d+)?([eE][+-]?\d+)?"
    SeparatorsPattern = r"^[^ \t\(\)\+\-\*/;,=\[\]{}<>'.:]*"

    StringToken = "STRING"
    FloatToken = "FLOAT"
    IntegerToken = "INTEGER"
    IdentifierToken = "IDENTIFIER"
    BadToken = "BAD"

    def __init__(self, file_path):
        self.file_path = file_path
        self.reader = open(file_path, "r", encoding="utf-8")
        self.line_number = 0
        self.column_number = 1
        self.line = ""
        self.is_eof = False

    def get_next_token(self):
        while not self.is_eof or self.line:
            if not self.line:
                self.read_next_line()
                if self.is_eof:
                    return None

            self.skip_whitespaces()

            if not self.line:
                continue

            if self.line.startswith("//"):
                self.line = ""
                continue

            if self.line.startswith("{"):
                result = self.parse_block_comment()
                if result:
                    return result
                continue

            if self.line.startswith("'"):
                return self.parse_string_literal()

            number_match = re.match(self.NumberPattern, self.line)
            if number_match:
                return self.parse_number_literal(number_match)

            identifier_match = re.match(self.IdentifierPattern, self.line)
            if identifier_match:
                return self.parse_identifier(identifier_match.group())

            for oper, token_type in Operator.Operators.items():
                if self.line.startswith(oper):
                    self.line = self.line[len(oper):]
                    self.column_number += len(oper)
                    return Token(token_type, oper, self.line_number, self.column_number - len(oper))

            if not re.match(r"^[a-zA-Z0-9_]*$", self.line):
                bad_match = re.match(self.SeparatorsPattern, self.line)
                if bad_match:
                    bad_lexeme = bad_match.group()
                    self.line = self.line[len(bad_lexeme):]
                    self.column_number += len(bad_lexeme)
                    return Token(self.BadToken, bad_lexeme, self.line_number, self.column_number - len(bad_lexeme))
        return None

    def parse_identifier(self, lexeme):
        if len(lexeme) > 256:
            self.line = self.line[len(lexeme):]
            self.column_number += len(lexeme)

            return Token(self.BadToken, lexeme, self.line_number, self.column_number - len(lexeme))

        if KeyWord.is_token(lexeme):
            token_type = lexeme.upper()
        else:
            token_type = self.IdentifierToken
        token = Token(token_type, lexeme, self.line_number, self.column_number)

        self.line = self.line[len(lexeme):]
        self.column_number += len(lexeme)
        self.line = self.line.replace("\n", "")

        if self.line and not re.match(r"[ \t\(\)\+\-\*/;,=\[\]{}<>'.:]", self.line[0]) and not re.match(
                r"^[a-zA-Z0-9_]*$", self.line):
            self.column_number -= len(lexeme)

            bad_token = Token(self.BadToken, lexeme + self.line, self.line_number, self.column_number)
            self.line = ""

            return bad_token

        return token

    def parse_number_literal(self, match):
        lexeme = match.group()

        if ('.' in lexeme and match.group(2) == '') or (lexeme.isdigit() and len(lexeme) > 16):
            self.line = self.line[len(lexeme):]
            self.column_number += len(lexeme)

            return Token(self.BadToken, lexeme, self.line_number, self.column_number - len(lexeme))

        if len(self.line) > len(lexeme) and not re.match(r"[ \t\n\(\)\+\-\*/;,=\[\]{}<>'.:0-9]", self.line[len(lexeme)]):
            bad_match = re.match(r"^[a-zA-Z0-9_]*", self.line)

            bad_token = Token(self.BadToken, self.line, self.line_number, self.column_number)
            self.line = self.line[len(bad_match.group()):]
            self.column_number += len(bad_match.group())

            return bad_token

        token_type = self.FloatToken if '.' in lexeme or 'e' in lexeme.lower() else self.IntegerToken

        self.line = self.line[len(lexeme):]
        self.column_number += len(lexeme)

        return Token(token_type, lexeme, self.line_number, self.column_number - len(lexeme))

    def parse_string_literal(self):
        match = re.match(self.StringPattern, self.line)
        if match:
            lexeme = match.group()
            self.line = self.line[len(lexeme):]
            self.column_number += len(lexeme)
            return Token(self.StringToken, lexeme, self.line_number, self.column_number - len(lexeme))

        lexeme = self.line.replace("\n", "")
        self.line = ""
        return Token(self.BadToken, lexeme, self.line_number, self.column_number)

    def parse_block_comment(self):
        temp = self.line.replace("\n", "")
        start_line_number = self.line_number
        start_column_number = self.column_number

        while True:
            end_index = self.line.find("}")
            if end_index != -1:
                self.line = self.line[end_index + 1:]
                self.column_number += end_index + 1
                break

            self.read_next_line()
            if self.is_eof:
                self.line = ""
                return Token(self.BadToken, temp, start_line_number, start_column_number)
            temp += "\n" + self.line.replace("\n", "")


    def skip_whitespaces(self):
        whitespaces = len(self.line) - len(self.line.lstrip())
        self.line = self.line.lstrip()
        self.column_number += whitespaces

    def read_next_line(self):
        self.line = self.reader.readline()
        if not self.line:
            self.is_eof = True
            self.line = ""
        else:
            self.line_number += 1
        self.column_number = 1


def main():
    if len(sys.argv) != 3:
        print("Usage: PascalLexer <input_file> <output_file>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lexer = Lexer(input_file)
    with open(output_file, "w", encoding="utf-8") as writer:
        while True:
            token = lexer.get_next_token()
            if token is None:
                break

            print(token)
            writer.write(str(token) + "\n")


if __name__ == "__main__":
    main()