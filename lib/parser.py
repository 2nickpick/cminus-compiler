#
#
#   Recursive Descent Parser
#   This module contains functions and objects for use by the Recursive Descent Parser
#
#
import sys
import inspect


class Parser(object):

    # static variables

    # initialization of properties
    def __init__(self, tokens):
        self.indentation = 0
        self.tokens = tokens
        self.debug = False
        self.accepted = True

        self.last_token = None
        self.current_token = self.tokens.pop()

    # Process input tokens for parsing
    # Start the recursive descent parsing
    def parse(self):
        self.program()

        # if self.debug:
        #     print(self.tokens)

        if len(self.tokens) == 0 and self.accepted is True:
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
            self.type_specifier()
            self.match("IDENTIFIER")

            if self.current_token == ["(", "OPERATORS"]:
                self.function_declaration()
            elif self.current_token and self.current_token[0] in ['[', ';']:
                self.var_declaration()

        self.end()

    # var-declaration -> type-specifier ID ; | type-specifier ID [ NUM ] ; | type-specifier ID [ FLOAT ] ;
    def var_declaration(self):
        self.start()
        if self.current_token == ['[', 'OPERATORS']:
            self.match("OPERATORS", "[")
            self.any_number()
            self.match("OPERATORS", "]")

        self.match("OPERATORS", ";")

        self.end()

    # function-declaration -> type-specifier ( params ) compound-statement
    def function_declaration(self):
        self.start()
        self.match("OPERATORS", "(")
        self.params()
        self.match("OPERATORS", ")")
        self.compound_statement()
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

        if self.current_token == ["void", "KEYWORD"]:
            self.match("KEYWORD", "void")
        else:
            self.params_list()

        self.end()

    # params-list -> params-list , param | param
    def params_list(self):
        self.start()

        self.param()
        while self.current_token == [",", "OPERATORS"]:
            self.match("OPERATORS", ",")
            self.param()

        self.end()

    # param -> type-specifier ID | type-specifier ID [ NUM ]
    def param(self):

        self.start()

        self.type_specifier()
        self.match("IDENTIFIER")

        if self.current_token == ['[', "OPERATORS"]:
            self.match('OPERATORS', '[')
            self.match('OPERATORS', ']')

        self.end()

    # compound-statement -> { local-declarations statement-list }
    def compound_statement(self):
        self.start()
        self.match("OPERATORS", "{")
        self.local_declarations()
        self.statement_list()
        self.match("OPERATORS", "}")
        self.end()

    # local-declarations -> local-declarations var-declaration | @
    def local_declarations(self):
        self.start()
        while self.current_token and self.current_token[0] in ["int", "float", "void"]:
            self.type_specifier()
            self.match("IDENTIFIER")
            self.var_declaration()

        self.end()

    # statement-list -> statement-list statement | @
    def statement_list(self):
        self.start()
        while self.current_token and self.current_token[0] != "}":
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
            self.expression()
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
        while self.current_token and self.current_token[0] in ['<=', '<', '>', '>=', '==', '!=']:
            self.relational_operation()
            self.additive_expression()

        self.end()

    # additive-expression -> term | add-operation term additive-expression
    def additive_expression(self):

        self.start()

        self.term()
        while self.current_token and self.current_token[0] in ["+", "-"]:
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
        while self.current_token and self.current_token[0] in ["*", "/"]:
            self.multiply_operation()
            self.factor()

        self.end()

    # factor -> ( expression ) | call | var | NUM | FLOAT
    def factor(self):
        self.start()
        if self.current_token == ["(", "OPERATORS"]:
            if self.last_token and self.last_token[1] == "IDENTIFIER":
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
        if self.current_token and self.current_token[1] == "IDENTIFIER":
            self.match("IDENTIFIER")
        if self.current_token == ["(", "OPERATORS"]:
            self.call()
        else:
            self.var()

        self.end()

    # call -> ( args )
    def call(self):
        self.start()

        self.match("OPERATORS", "(")
        self.args()
        self.match("OPERATORS", ")")

        self.end()

    # var -> [ expression ] | @
    def var(self):

        self.start()

        if self.current_token == ["[", "OPERATORS"]:
            self.match("OPERATORS", "[")
            self.expression()
            self.match("OPERATORS", "]")

        self.end()

    # args -> args-list | @
    def args(self):

        self.start()

        if self.current_token != [")", "OPERATORS"]:
            self.arg_list()

        self.end()

    # arg-list -> expression | expression , arg-list
    def arg_list(self):

        self.start()
        self.expression()
        while self.current_token == [",", "OPERATORS"]:
            self.match("OPERATORS", ",")
            self.expression()

        self.end()

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

    # an error has occured, reject the input
    def reject(self, token_type, token_value):
        self.accepted = False
        print("REJECT", end="",flush=True)
        if self.debug:
            print("Current Token: " + str(self.current_token))
            print("Failed to match [" + str(token_type) + ", " + str(token_value) + "] in " + str(inspect.stack()[2][3]))
        sys.exit()

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

