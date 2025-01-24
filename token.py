class Operator:
    Operators = {
        ":=": "ASSIGN",
        "<=": "LESS_EQ",
        ">=": "GREATER_EQ",
        "<>": "NOT_EQ",
        "*": "MULTIPLICATION",
        "+": "PLUS",
        "-": "MINUS",
        "/": "DIVIDE",
        ";": "SEMICOLON",
        ",": "COMMA",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        "[": "LEFT_BRACKET",
        "]": "RIGHT_BRACKET",
        "=": "EQ",
        ">": "GREATER",
        "<": "LESS",
        ".": "DOT",
        ":": "COLON",
    }

    @staticmethod
    def is_token(token: str) -> bool:
        return token in Operator.Operators


class Token:
    def __init__(self, token_type: str, value: str, line: int, column: int):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.length = len(value)

    def __str__(self):
        return f"{self.token_type} ({self.line}, {self.column}) \"{self.value}\""


class KeyWord:
    Keywords = [
        "ARRAY",
        "BEGIN",
        "ELSE",
        "END",
        "IF",
        "OF",
        "OR",
        "PROGRAM",
        "PROCEDURE",
        "THEN",
        "TYPE",
        "VAR",
    ]

    @staticmethod
    def is_token(word: str) -> bool:
        return word.upper() in KeyWord.Keywords
