#
#
#   Main
#   This module acts as the starting point for the lexical analysis
#
#   The goal of this project is to tokenize a potential C- program, and sanitize the tokens for
#   passing to the parser.
#
#

import sys
from lib import util
from lib import lexical_analyzer

__author__ = 'Nicholas Pickering'

filename = 0

#   Start Main Program
print("Lexical Analyzer")
print("Written by Nicholas Pickering")

#   Read in file for processing...
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    util.error("No filename specified... Exiting...", True)

file = open(filename, "r")
if not file:
    util.error("File could not be loaded... Exiting...", True)

#
#   Process File for Tokens
#

for line in file.readlines():
    line = line.replace("\n", "").replace("\t", "").strip() + " "

    if len(line) <= 1:
        continue

    print("\nINPUT: " + line)

    #
    #   Begin Line-by-Line Processing
    #
    current_position_in_line = 0
    while current_position_in_line < len(line):

        char = line[current_position_in_line]
        token_complete = False
        lexical_analyzer.token_type = ""

        # Determine a potential token type
        if char is "/":
            lexical_analyzer.token_type = "OPERATOR_OR_COMMENT"

        elif char is "*":
            lexical_analyzer.token_type = "OPERATOR_OR_END_COMMENT"

        elif char.isalpha():
            lexical_analyzer.token_type = "KEYWORD_OR_IDENTIFIER"

        elif char.isdigit():
            lexical_analyzer.token_type = "NUMBER"

        elif char == ".":
            lexical_analyzer.token_type = "FLOAT"

        elif char is " ":
            lexical_analyzer.token_type = "SPACE"
            lexical_analyzer.active_token = ""

            token_complete = True
            lexical_analyzer.process_complete_token()

            current_position_in_line += 1

        elif char in lexical_analyzer.extendable_operators:
            lexical_analyzer.token_type = "OPERATORS"

        elif char in lexical_analyzer.operators:
            lexical_analyzer.token_type = "OPERATORS"

            lexical_analyzer.active_token = char
            lexical_analyzer.process_complete_token()

            current_position_in_line += 1
            token_complete = True

        else:
            lexical_analyzer.token_type = "ERROR"

        lexical_analyzer.active_token = char

        # If token is not a single-character token, let's begin collecting characters for the token
        while not token_complete:

            # let's prep the next character
            current_position_in_line += 1

            if current_position_in_line >= len(line):
                # if we've reached the end of the line, process the token as is
                if lexical_analyzer.token_type is "OPERATORS" and lexical_analyzer.active_token is "!":
                    lexical_analyzer.token_type = "ERROR"

                token_complete = True
                lexical_analyzer.process_complete_token()
                break

            # Process the next character into the token
            char = line[current_position_in_line]

            if lexical_analyzer.token_type is "OPERATOR_OR_COMMENT":
                if char is "*":  # multi line comment
                    lexical_analyzer.comment_nesting_level += 1
                    lexical_analyzer.active_token += char
                    current_position_in_line += 1
                    lexical_analyzer.token_type = "COMMENT"
                    token_complete = True
                elif char is "/":  # single line comment
                    lexical_analyzer.active_token += char
                    token_complete = True
                    current_position_in_line = len(line)
                    lexical_analyzer.token_type = "COMMENT"
                else:
                    lexical_analyzer.token_type = "OPERATORS"
                    token_complete = True

                # end of the line, pass the token on
                if current_position_in_line + 1 >= len(line):
                    token_complete = True

            elif lexical_analyzer.token_type is "OPERATORS":
                if char is "=":  # extended operator
                    lexical_analyzer.active_token += char
                    current_position_in_line += 1
                    token_complete = True
                elif lexical_analyzer.active_token is "!":
                    lexical_analyzer.token_type = "ERROR"
                    token_complete = True
                else:
                    token_complete = True

            elif lexical_analyzer.token_type is "OPERATOR_OR_END_COMMENT":

                if char is "/":  # end of multiline comment
                    if lexical_analyzer.comment_nesting_level > 0:
                        lexical_analyzer.comment_nesting_level -= 1
                        lexical_analyzer.active_token = ""
                        current_position_in_line += 1
                    else:
                        lexical_analyzer.token_type = "OPERATORS"

                    token_complete = True

                else:
                    lexical_analyzer.token_type = "OPERATORS"
                    token_complete = True

                # end of the line, pass the token on
                if current_position_in_line + 1 >= len(line):
                    token_complete = True

            elif lexical_analyzer.token_type is "KEYWORD_OR_IDENTIFIER":
                if char.isalpha():  # string is still being built
                    lexical_analyzer.active_token += char
                else:  # this is the end of the string
                    token_complete = True

                # end of the line, pass the token on
                if current_position_in_line + 1 >= len(line):
                    token_complete = True

            elif lexical_analyzer.token_type is "NUMBER":
                if char.isdigit() or char is ".":  # number is still being built
                    lexical_analyzer.active_token += char
                else:  # this is the end of the string
                    token_complete = True

                if "." in lexical_analyzer.active_token:
                    lexical_analyzer.token_type = "FLOAT"

            elif lexical_analyzer.token_type is "FLOAT":
                if char.isdigit() or char is "." or char is "E":  # number is still being built
                    lexical_analyzer.active_token += char
                elif "E" in lexical_analyzer.active_token:
                    if char.isdigit() or char is "-":  # number is still being built
                        lexical_analyzer.active_token += char
                    else:
                        token_complete = True
                else:  # this is the end of the string
                    token_complete = True

            elif lexical_analyzer.token_type is "ERROR":
                if char not in [" "] + lexical_analyzer.operators + lexical_analyzer.extendable_operators:
                    lexical_analyzer.active_token += char
                else:
                    token_complete = True

            else:
                token_complete = True

            # process a completed token
            if token_complete:
                lexical_analyzer.process_complete_token()


print("---------------------------------------\n")

print("End Lexical Analysis")