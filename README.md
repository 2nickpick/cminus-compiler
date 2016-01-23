Nicholas Pickering
Contruction of Language Translators COP4620
Project 1 - Lexical Analyzer
Professor Eggen
Date Due: 1/26/2016
Date Submitted: 1/23/2016

# Introduction
This program is designed to tokenize a text file for valid tokens to be provided to a C- parser.

# Invoking the application
Invoke the application by calling:
    ./p1 filename

    where filename is the path to the C- program to tokenize.

# Main
The entry point to the application is main.py.

# Program Flow
The input file is processed line by line, character by character. At the beginning of a new token, the analyzer
determines the type (or set of types) the new token may belong to.

The analyzer then accepts characters until a character is found which does not comply with the determined
token type, handling errors as necessary.

The output result is a listing of tokens as they are recognized. A token collection is ready to be passed
to a language parser.

Nested comments and Floating point numbers are supported.

# Output Files
This program produces output to the console.

An example result set for my initial test is saved to the output directory.
