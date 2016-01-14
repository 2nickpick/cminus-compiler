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

comment_nesting_level = 0
for line in file.readlines():
    line = line.replace("\n", "").replace("\t", "")

    if len(line) <= 0:
        continue

    print("INPUT: " + line)

    active_token = ""  # token currently being built by the lexical analyzer
    for char in line:
        # Process comments
        if active_token == "/":
            if char == "*":
                comment_nesting_level += 1
                print("We do have a comment! Nesting Level: " + str(comment_nesting_level))
                active_token = ""
                continue
            else:
                print("Nope, not a comment... keep moving...")

        if active_token == "*":
            if char == "/":
                comment_nesting_level -= 1
                print("We are closing a comment! Nesting Level: " + str(comment_nesting_level))
                active_token = ""
                continue
            else:
                print("Nope, we are still in a comment... keep moving...")

        if char == "/":
            print("We may have a comment...")
            active_token += char

        elif char == "*":
            print("We may be closing a comment...")
            active_token += char

        elif char.isalpha():
            active_token += char


print("---------------------------------------\n")

print("End Lexical Analysis")


