#
#
#   Recursive Descent Parser
#   This module contains functions and objects for use by the Recursive Descent Parser
#
#
from __future__ import print_function
import sys
import inspect
from lib import symbol_table


class Parser(object):

    # static variables

    # initialization of properties
    def __init__(self, tokens):
        self.indentation = 0
        self.tokens = tokens
        self.debug = False
        self.debug_semantics = True
        self.accepted = True
        self.symbol_table = symbol_table.SymbolTable()
        self.current_symbol = None
        self.scope = 0

        self.parsing_main = False
        self.main_function_exists = False

        self.found_void_type = False
        self.parsing_void_function = False

        self.found_int_type = False
        self.parsing_int_function = False

        self.found_float_type = False
        self.parsing_float_function = False

        self.last_token = None
        self.current_token = self.tokens.pop()

        self.calling_function = None  # name of function currently parsing args for
        self.function_params = []  # list of params for a function
        self.args_parsed = 0  # number of passed args, for catching mismatched params

    # Process input tokens for parsing
    # Start the recursive descent parsing
    def parse(self):
        self.program()

        # if self.debug:
        #     print(self.tokens)

        self.symbol_table.destroy_scope(0)

        if not self.main_function_exists:
            self.reject_semantic("Main function undefined")

        if self.debug_semantics:
            for symbol in self.symbol_table.symbols:
                print(str(symbol))

        if len(self.tokens) == 0 and self.current_token is None and self.accepted is True:
            if self.debug:
                print(self.tokens)
            return 'ACCEPT'
        else:
            return 'REJECT'

    # program -> declaration-list
    def program(self):
        self.start()
        self.declaration_list()
        self.end()

    # declaration-list -> var-declaration | function-declaration | empty-declaration
    def declaration_list(self):
        self.start()
        while len(self.tokens) > 0 and self.accepted is not False:
            self.declaration()
        self.end()

    # declaration -> type-specifier ID ; | type-specifier ID [ NUM ] ;
    def declaration(self):
        self.start()

        if self.current_token == [";", "OPERATORS"]:
            self.empty_declaration()
        else:
            self.current_symbol = symbol_table.Symbol()
            self.current_symbol.set_type(self.current_token[0])
            self.current_symbol.set_scope(self.scope)

            if self.current_token[0] == "void":
                self.found_void_type = True
            if self.current_token[0] == "int":
                self.found_int_type = True
            if self.current_token[0] == "float":
                self.found_float_type = True

            self.type_specifier()

            self.current_symbol.set_identifier(self.current_token[0])
            if self.current_token[0] == "main":
                self.parsing_main = True

            self.match("IDENTIFIER")

            if self.current_token == ["(", "OPERATORS"]:
                self.current_symbol.set_is_function(True)

            if not self.symbol_table.add_symbol(self.current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + self.current_symbol.identifier)

            self.current_symbol = None

            if self.current_token == ["(", "OPERATORS"]:
                if self.found_void_type:
                    self.parsing_void_function = True
                if self.found_int_type:
                    self.parsing_int_function = True
                if self.found_float_type:
                    self.parsing_float_function = True

                self.function_declaration()

                self.found_void_type = False
                self.parsing_void_function = False
                self.found_int_type = False
                self.parsing_int_function = False
                self.found_float_type = False
                self.parsing_float_function = False

            elif self.current_token and self.current_token[0] in ['[', ';']:
                self.var_declaration()

            self.parsing_main = False

        self.end()

    # var-declaration -> type-specifier ID ; | type-specifier ID [ NUM ] ; | type-specifier ID [ FLOAT ] ;
    def var_declaration(self):
        self.start()
        if self.current_token == ['[', 'OPERATORS']:
            self.match("OPERATORS", "[")
            self.integer()
            self.match("OPERATORS", "]")

        self.match("OPERATORS", ";")

        self.end()

    # function-declaration -> type-specifier ( params ) compound-statement
    def function_declaration(self):
        self.start()

        self.calling_function = self.last_token[0]

        self.match("OPERATORS", "(")
        self.params()
        self.match("OPERATORS", ")")
        self.compound_statement()

        if self.parsing_main is True and self.accepted is not False:
            self.main_function_exists = True

        self.calling_function = None

        self.end()

    # type-specifier -> int | void | float
    def type_specifier(self):
        self.start()
        if self.current_token == ["int", "KEYWORD"]:
            self.match("KEYWORD", "int")
        elif self.current_token == ["void", "KEYWORD"]:
            self.match("KEYWORD", "void")
        else:
            self.match("KEYWORD", "float")

        self.end()

    # integer -> NUM
    def integer(self):
        self.start()
        self.match("NUMBER")
        self.end()

    # any-number -> NUM | FLOAT
    def any_number(self):
        self.start()

        if self.current_token and self.current_token[1] == "NUMBER":
            self.match("NUMBER")
        else:
            self.match("FLOAT")

        self.end()

    # params -> void | params-list
    def params(self):
        self.start()

        self.params_list()

        self.end()

    # params-list -> params-list , param | param
    def params_list(self):
        self.start()

        self.param()
        while self.current_token == [",", "OPERATORS"] \
                and self.accepted is not False:
            self.match("OPERATORS", ",")
            self.param()

        self.end()

    # param -> type-specifier ID | type-specifier ID [ NUM ]
    def param(self):

        self.start()

        self.current_symbol = symbol_table.Symbol()
        self.current_symbol.set_type(self.current_token[0])
        self.current_symbol.set_scope(self.scope+1)
        self.current_symbol.set_parent(self.calling_function, self.scope)

        is_void = self.current_token == ["void", "KEYWORD"]

        self.type_specifier()

        is_void_with_identifier = is_void and \
            self.current_token and self.current_token[1] == "IDENTIFIER"

        if not is_void or is_void_with_identifier:
            self.current_symbol.set_identifier(self.current_token[0])

            if is_void_with_identifier and self.current_token[1] is "IDENTIFIER":
                self.reject_semantic("Void parameter cannot be named: " + str(self.calling_function) + ", " + self.current_token[0])
            self.match("IDENTIFIER")

            if not self.symbol_table.add_symbol(self.current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + self.current_symbol.identifier)

        self.current_symbol = None

        if self.current_token == ['[', "OPERATORS"]:
            self.match('OPERATORS', '[')
            self.match('OPERATORS', ']')

        self.end()

    # compound-statement -> { local-declarations statement-list }
    def compound_statement(self):
        self.start()
        self.match("OPERATORS", "{")
        self.scope += 1
        self.local_declarations()
        self.statement_list()
        self.match("OPERATORS", "}")
        self.symbol_table.destroy_scope(self.scope)
        self.scope -= 1
        self.end()

    # local-declarations -> local-declarations var-declaration | @
    def local_declarations(self):
        self.start()
        while self.current_token and self.current_token[0] in ["int", "float", "void"] \
                and self.accepted is not False:

            self.current_symbol = symbol_table.Symbol()
            self.current_symbol.set_type(self.current_token[0])
            self.current_symbol.set_scope(self.scope)

            is_void = self.current_token and self.current_token == ["void", "KEYWORD"]

            self.type_specifier()

            if is_void and self.current_token and self.current_token[1] is "IDENTIFIER":
                self.reject_semantic("variables with type void are not permitted: " + str(self.current_token[0]))

            self.current_symbol.set_identifier(self.current_token[0])
            self.match("IDENTIFIER")
            self.var_declaration()

            if not self.symbol_table.add_symbol(self.current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + self.current_symbol.identifier)

            self.current_symbol = None

        self.end()

    # statement-list -> statement-list statement | @
    def statement_list(self):
        self.start()
        while self.current_token and self.current_token[0] != "}" and self.accepted is not False:
            self.statement()

        self.end()

    # statement -> expression-statement | selection-statement | compound-statement
    #   | iteration-statement | return-statement | empty-statement
    def statement(self):
        self.start()
        if self.current_token[0] == "if":
            self.selection_statement()
        elif self.current_token[0] == "while":
            self.iteration_statement()
        elif self.current_token[0] == "return":
            self.return_statement()
        elif self.current_token[0] == "{":
            self.compound_statement()
        elif self.current_token[0] == ";":
            self.empty_statement()
        else:
            self.expression_statement()

        self.end()

    # selection-statement -> if ( expression ) statement | if ( expression ) statement else statement
    def selection_statement(self):
        self.start()
        self.match("KEYWORD", "if")
        self.match("OPERATORS", "(")
        self.expression()
        self.match("OPERATORS", ")")
        self.statement()
        if self.current_token and self.current_token[0] == "else":
            self.match("KEYWORD", "else")
            self.statement()

        self.end()

    # iteration-statement -> while ( expression ) statement
    def iteration_statement(self):

        self.start()

        self.match("KEYWORD", "while")
        self.match("OPERATORS", "(")
        self.expression()
        self.match("OPERATORS", ")")
        self.statement()

        self.end()

    # return-statement -> return expression ; | return ;
    def return_statement(self):

        self.start()

        self.match("KEYWORD", "return")
        if self.current_token != [';', 'OPERATORS']:
            if self.parsing_void_function:
                self.reject_semantic("Void function should not have a return value.")

            # check that expression returned is an integer
            #if self.parsing_int_function:
            #    self.reject_semantic("Int function needs an int return value")

            # check that expression returned is a float
            #elif self.parsing_float_function:
            #    self.reject_semantic("Float function needs a float return value")

            self.expression()
        #else:
            #if self.parsing_int_function:
            #    self.reject_semantic("Int function needs an int return value")
            #elif self.parsing_float_function:
            #    self.reject_semantic("Float function needs a float return value")

        self.match("OPERATORS", ";")

        self.end()

    # expression-statement -> expression ;
    def expression_statement(self):

        self.start()

        self.expression()
        self.match("OPERATORS", ";")

        self.end()

    # empty-statement -> ;
    def empty_statement(self):

        self.start()

        self.match("OPERATORS", ";")

        self.end()

    # empty-declaration -> ;
    def empty_declaration(self):

        self.start()

        self.match("OPERATORS", ";")

        self.end()

    # assignment-statement -> = expression
    def assignment_statement(self):

        self.start()

        self.match("OPERATORS", "=")
        self.expression()

        self.end()

    # expression -> ID var assignment-expression | simple-expression
    def expression(self):
        self.start()

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            if not self.symbol_table.exists(self.current_token[0], self.scope):
                self.reject_semantic("Undeclared identifier: " + self.current_token[0])

            self.match("IDENTIFIER")
            self.var()
            if self.current_token and self.current_token[0] == "=":
                self.assignment_statement()
            else:
                self.simple_expression()
        else:
            self.simple_expression()

        self.end()

    # simple-expression -> additive-expression relational-expression
    def simple_expression(self):

        self.start()

        self.additive_expression()
        self.relational_expression()

        self.end()

    # relational-expression -> relational-operation additive expression relational-operation | @
    def relational_expression(self):

        self.start()
        while self.current_token and self.current_token[0] in ['<=', '<', '>', '>=', '==', '!='] \
                and self.accepted is not False:
            self.relational_operation()
            self.additive_expression()

        self.end()

    # additive-expression -> term | add-operation term additive-expression
    def additive_expression(self):

        self.start()

        self.term()
        while self.current_token and self.current_token[0] in ["+", "-"] \
                and self.accepted is not False:
            self.add_operation()
            self.term()

        self.end()

    # add-operation -> + | -
    def add_operation(self):

        self.start()

        if self.current_token == ['+', 'OPERATORS']:
            self.match("OPERATORS", "+")
        else:
            self.match("OPERATORS", "-")

        self.end()

    # multiply-operation -> * | /
    def multiply_operation(self):

        self.start()
        if self.current_token == ['*', 'OPERATORS']:
            self.match("OPERATORS", "*")
        else:
            self.match("OPERATORS", "/")

        self.end()

    # relational-operation -> <= | < | > | >= | == | !=
    def relational_operation(self):
        self.start()
        if self.current_token == ['<=', 'OPERATORS']:
            self.match("OPERATORS", "<=")
        elif self.current_token == ['<', 'OPERATORS']:
            self.match("OPERATORS", "<")
        elif self.current_token == ['>', 'OPERATORS']:
            self.match("OPERATORS", ">")
        elif self.current_token == ['>=', 'OPERATORS']:
            self.match("OPERATORS", ">=")
        elif self.current_token == ['==', 'OPERATORS']:
            self.match("OPERATORS", "==")
        else:
            self.match("OPERATORS", "!=")

        self.end()

    # term -> factor | factor multiply-operation factor term
    def term(self):

        self.start()
        self.factor()
        while self.current_token and self.current_token[0] in ["*", "/"] \
                and self.accepted is not False:
            self.multiply_operation()
            self.factor()

        self.end()

    # factor -> ( expression ) | call | var | NUM | FLOAT
    def factor(self):
        self.start()
        if self.current_token == ["(", "OPERATORS"]:
            if self.last_token and self.last_token[1] == "IDENTIFIER":
                if not self.symbol_table.function_exists(self.last_token[0], self.scope):
                    self.reject_semantic("" + self.last_token[0] + " is not a function")

                self.calling_function = self.last_token[0]
                self.call()
            else:
                self.match("OPERATORS", "(")
                self.expression()
                self.match("OPERATORS", ")")
        elif self.current_token and self.current_token[1] in ["NUMBER", "FLOAT"]:
            self.any_number()
        else:
            self.call_or_var()

        self.end()

    # call-or-var -> ID | call | var
    def call_or_var(self):
        self.start()

        self.calling_function = self.last_token[0]

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            self.match("IDENTIFIER")
            self.calling_function = self.last_token[0]

        if self.current_token == ["(", "OPERATORS"]:
            self.call()
        else:
            self.var()

        self.calling_function = None

        self.end()

    # call -> ( args )
    def call(self):
        self.start()

        called_function = self.calling_function

        function_params = self.symbol_table.load_params(self.calling_function, self.scope)

        self.match("OPERATORS", "(")
        args_parsed = self.args()
        self.match("OPERATORS", ")")

        if len(args_parsed) != len(function_params):
            self.reject_semantic("Mismatched number of arguments for '" + str(called_function) + "'. Found " +
                                 str(len(args_parsed)) + ", Expected " + str(len(function_params)))

        self.end()

    # var -> [ expression ] | @
    def var(self):

        self.start()

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            self.match("IDENTIFIER")
            self.var()

        if self.last_token and self.last_token[1] == "IDENTIFIER" and self.current_token[0] != "(":
            if not self.symbol_table.var_exists(self.last_token[0], self.scope):
                self.reject_semantic("" + self.last_token[0] + " is a function, not a variable")

        if self.current_token == ["[", "OPERATORS"]:
            self.match("OPERATORS", "[")
            self.expression()
            self.match("OPERATORS", "]")

        self.end()

    # args -> args-list | @
    def args(self):

        self.start()

        return_args = []

        if self.current_token != [")", "OPERATORS"]:
            return_args = self.arg_list()

        self.end()

        return return_args

    # arg-list -> expression | expression , arg-list
    def arg_list(self):

        self.start()

        return_args = [self.expression()]

        while self.current_token == [",", "OPERATORS"] \
                and self.accepted is not False:
            self.match("OPERATORS", ",")
            return_args.append(self.expression())

        self.end()

        return return_args

    # accept a token out from the input stream
    def match(self, token_type, token_value=None):
        # if self.debug:
        #     if token_value is None:
        #         print("Check if current token is any token of type '" + token_type + "'")
        #     else:
        #         print("Check if current token is a '" + token_type + "' with a value of " + str(token_value))
        #
        #     print(self.current_token)

        if self.current_token is not None and self.current_token[1] == token_type:
            if token_value is not None:
                if self.current_token[0] == token_value:
                    if self.debug:
                        print("\t"*self.indentation + "Token matched (by value): " + str(self.current_token))
                    self.next_token()
                    return
            else:
                if self.debug:
                    print("\t"*self.indentation + "Token matched (by type): " + str(self.current_token))
                self.next_token()
                return

        self.reject(token_type, token_value)

    # advance the parser to the next token
    def next_token(self):
        self.last_token = self.current_token
        if len(self.tokens) > 0:
            self.current_token = self.tokens.pop()
        else:
            self.current_token = None
            return

    # an error has occurred, reject the input
    def reject(self, token_type, token_value):
        self.accepted = False
        if self.debug:
            print("Current Token: " + str(self.current_token))
            print("Failed to match [" + str(token_type) + ", " + str(token_value) + "] in " + str(inspect.stack()[2][3]))

    # a semantic error has occurred, reject the input
    def reject_semantic(self, reason):
        if self.accepted is True and self.debug_semantics:
            print("Semantic Rejection: " + reason)
        self.accepted = False

    # debug output for entering a recursive function
    def start(self):
        if self.debug:
            print(("\t"*self.indentation) + "Starting '" + inspect.stack()[1][3] + "'...")
            self.indentation += 1

    # debug output for exiting a recursive function
    def end(self):
        if self.debug:
            self.indentation -= 1
            print(("\t"*self.indentation) + "Ending '" + inspect.stack()[1][3] + "'...")

