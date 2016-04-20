#
#
#   Main
#   This module acts as the starting point for the lexical analysis
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
from lib.prettytable import PrettyTable

__author__ = 'Nicholas Pickering'

filename = 0

#   Start Main Program
# print("Recursive Descent Parser")
# print("Written by Nicholas Pickering")

#   Read in file for processing...
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    util.error("No filename specified... Exiting...", True)

file = open(filename, "r")
if not file:
    util.error("File could not be loaded... Exiting...", True)

lexical_analyzer = LexicalAnalyzer()
tokens = lexical_analyzer.process_file(file)

if len(tokens) > 0:
    tokens.reverse()

parser = Parser(tokens)
parse_result = parser.parse()

table = PrettyTable(["i", "opcode", "operand1", "operand2", "result"])

table.align["i"] = "r" # Left align city names
table.align["opcode"] = "r" # Left align city names
table.align["operand1"] = "r" # Left align city names
table.align["operand2"] = "r" # Left align city names
table.align["result"] = "r" # Left align city names
for quadruple in parser.quadruples:
    table.add_row(quadruple)

print(table)

# print("---------------------------------------\n")
#
# print("End Parsing")
