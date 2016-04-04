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

    def add_symbol(self, symbol_to_add):
        if not self.exists_in_scope(symbol_to_add.identifier, symbol_to_add.scope):

            if symbol_to_add.parent is not None:
                for symbol in reversed(self.symbols):
                    if symbol_to_add.parent:
                        if symbol.identifier == symbol_to_add.parent[0] and symbol.scope <= symbol_to_add.scope:
                            symbol.parameters.append(symbol_to_add)
                            break

            self.symbols.append(symbol_to_add)

            return True
        else:
            return False

    def exists(self, identifier, scope):
        for symbol in reversed(self.symbols):
            if symbol.identifier == identifier and symbol.scope <= scope:
                return True

        return False

    def load_params(self, function_name, scope):
        for symbol in reversed(self.symbols):
            if symbol.identifier == function_name and symbol.scope <= scope:
                return symbol.parameters

        return []

    def function_exists(self, identifier, scope):
        for symbol in reversed(self.symbols):
            if symbol.identifier == identifier and symbol.scope <= scope:
                if not symbol.is_function:
                    # found matching symbol, but it is not a function
                    return False
                else:
                    # found matching symbol in closest scope, and is a function
                    return True

        # no match found
        return False

    def var_exists(self, identifier, scope):
        for symbol in reversed(self.symbols):
            if symbol.identifier == identifier and symbol.scope <= scope:
                if symbol.is_function:
                    # found matching symbol, but it is not a function
                    return False
                else:
                    # found matching symbol in closest scope, and is a function
                    return True

        # no match found
        return False

    def exists_in_scope(self, identifier, scope):
        for symbol in self.symbols:
            if symbol.identifier == identifier and symbol.scope == scope:
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
        self.is_function = False
        self.parent = None
        self.parameters = []

    def create(self, identifier, type, value, scope, is_function):
        self.identifier = identifier
        self.type = type
        self.value = value
        self.scope = scope
        self.is_function = is_function
        self.parent = None
        self.parameters = []

    def set_identifier(self, identifier):
        self.identifier = identifier

    def set_type(self, type):
        self.type = type

    def set_value(self, value):
        self.value = value

    def set_scope(self, scope):
        self.scope = scope

    def set_is_function(self, is_function):
        self.is_function = is_function

    def set_parent(self, identifier, scope):
        self.parent = [identifier, scope]

    def __str__(self):
        return str(self.identifier) + "\t" + str(self.type) + "\t" + str(self.value) + "\t" + str(self.scope) \
                + str(self.parent)

