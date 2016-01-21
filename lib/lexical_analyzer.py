#
#
#   Lexical Analyzer
#   This module contains functions and objects for use by the Lexical Analyzer
#
#

comment_nesting_level = 0
tokens = []
active_token = ""
token_type = ""

keywords = [
    "else",
    "if",
    "int",
    "return",
    "void",
    "while",
    "float",
    "break",
    "continue"
]

operators = [
    "+",
    "-",
    "*",
    "/",
    ";",
    ",",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}"
]

extendable_operators = [
    "<",
    ">",
    "!",  # NOTE: The bang (!) operator is invalid by itself, this is handled in the processing of the token
    "=",
]


def process_complete_token():
    global active_token, token_type
    active_token = active_token.strip()

    append_token = False

    if active_token is not "" and comment_nesting_level is 0:
        if token_type is "OPERATOR_OR_END_COMMENT":
            if active_token is "*":
                token_type = "OPERATORS"
                append_token = True
            else:
                token_type = "COMMENT"

        elif token_type in ["KEYWORD_OR_IDENTIFIER"]:
            append_token = True
            if active_token in keywords:
                token_type = "KEYWORD"
            else:
                token_type = "IDENTIFIER"

        elif token_type not in ["COMMENT", "SPACE"]:
            append_token = True

    if append_token:
        tokens.append([active_token, token_type])

        tabs = 2
        if token_type in ["IDENTIFIER"]:
            tabs = 1
        elif token_type in ["FLOAT", "ERROR"]:
            tabs = 3

        print("[" + token_type + "]" + ("\t" * tabs) + active_token)

    active_token = ""
