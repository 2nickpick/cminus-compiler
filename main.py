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

# list of keywords
keywords = [
    'int',
    'return',
    'if',
    'else',
    'void',
    'while',


]

tokens = [] # list of tokens determined from input file
comment_nesting_level = 0 # current level of comment nesting
for line in file.readlines():
    line = line.replace("\n", "").replace("\t", "")

    if len(line) <= 0:
        continue

    print("INPUT: " + line)

    active_token = ""  # token currently being built by the lexical analyzer
    for char in line:
        token_completed = False
        print("Char: " + char)

        # check if previously formed token is prepared to be added to list
        if active_token == "/":
            if char == "*":
                comment_nesting_level += 1
                print("We do have a comment! Nesting Level: " + str(comment_nesting_level))
                token_completed = True
            else:
                print("Nope, not a comment... keep moving...")

        elif active_token == "*":
            if char == "/":
                comment_nesting_level -= 1
                print("We are closing a comment! Nesting Level: " + str(comment_nesting_level))
                token_completed = True
            else:
                print("Nope, we are still in a comment... keep moving...")

        # Add characters to active token, if token isn't complete
        if char == "/":
            print("We may have a comment...")

        elif char == "*":
            print("We may be closing a comment...")

        elif char.isalpha():
            print("We have a keyword/identifier...")

            active_token += char

        if token_completed:
            active_token = ""

        print("Active Token: " + active_token + "\n")

        if token_completed:
            print("Token completed, \nActive Token: ")
            active_token = ""


print("---------------------------------------\n")

print("End Lexical Analysis")


