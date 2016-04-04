#
#
#   Test
#   Run Test Files
#
#   The goal of this project is to tokenize a potential C- program, and sanitize the tokens for
#   passing to the parser.
#
#

from __future__ import print_function
import sys
from lib import util
from lib.lexical_analyzer import LexicalAnalyzer
from lib.parser import Parser
import glob
__author__ = 'Nicholas Pickering'

filename = 0

#   Start Main Program
# print("Recursive Descent Parser")
# print("Written by Nicholas Pickering")

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    util.error("No test directory specified... Exiting...", True)

#   Read in file for processing...
files = glob.glob("data/" + str(sys.argv[1]) + "/*.txt")
no_errors = True
for filename in files:

    file = open(filename, "r")
    if not file:
        util.error("File could not be loaded... Exiting...", True)

    lexical_analyzer = LexicalAnalyzer()
    tokens = lexical_analyzer.process_file(file)

    if len(tokens) > 0:
        tokens.reverse()

    parser = Parser(tokens)
    parse_result = parser.parse()

    should_fail = "-fail" in filename
    error = False

    if should_fail and parse_result == "ACCEPT":
        error = True
    elif not should_fail and parse_result == "REJECT":
        error = True

    if error:
        if no_errors:
            print("Invalid Tests:")

        no_errors = False
        print(filename + ": " + parse_result + "\n", end="")

if no_errors:
    print("All Tests Passed!")
