#
#
#   Symbol Table for Semantic Analysis
#   This module contains functions and objects for use by the Recursive Descent Parser
#
#
from __future__ import print_function
import sys
import inspect

from lib.util import deepcopy


class SymbolTable(object):

    def __init__(self):
        self.symbols = []

    def add_symbol(self, symbol):
        if not self.exists(symbol.identifier, symbol.scope):
            self.symbols.append(symbol)
            return True
        else:
            return False

    def exists(self, identifier, scope):
        for symbol in self.symbols:
            if symbol.identifier == identifier and symbol.scope <= scope:
                return True

        return False

    def destroy_scope(self, scope):
        symbols_to_remove = []
        for symbol in self.symbols:
            if symbol.scope == scope:
                symbols_to_remove.append(symbol)

        for symbol_to_remove in symbols_to_remove:
            self.symbols.remove(symbol_to_remove)

        return True

    def __str__(self):
        return self.symbols.__str__()


class Symbol(object):

    def __init__(self):
        self.identifier = None
        self.type = None
        self.value = None
        self.scope = None

    def create(self, identifier, type, value, scope):
        self.identifier = identifier
        self.type = type
        self.value = value
        self.scope = scope

    def set_identifier(self, identifier):
        self.identifier = identifier

    def set_type(self, type):
        self.type = type

    def set_value(self, value):
        self.value = value

    def set_scope(self, scope):
        self.scope = scope

    def __str__(self):
        return str(self.identifier) + "\t" + str(self.type) + "\t" + str(self.value) + "\t" + str(self.scope)

