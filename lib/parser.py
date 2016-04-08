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

        # code generation
        self.quadruples = []  # generated opcodes
        self.temps = []  # temporary variables needed for code generation
        self.backpatches = []  # codes in table needed to be patched

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
            current_symbol = symbol_table.Symbol()
            type = self.current_token[0]
            current_symbol.set_scope(self.scope)
            array_info = [False, 0]

            if self.current_token[0] == "void":
                self.found_void_type = True
            if self.current_token[0] == "int":
                self.found_int_type = True
            if self.current_token[0] == "float":
                self.found_float_type = True

            self.type_specifier()

            identifier = self.current_token[0]
            current_symbol.set_identifier(identifier)
            if self.current_token[0] == "main":
                self.parsing_main = True

            self.match("IDENTIFIER")

            if self.current_token == ["[", "OPERATORS"]:
                type += "[]"

            current_symbol.set_type(type)

            is_function = False
            if self.current_token == ["(", "OPERATORS"]:
                is_function = True
                current_symbol.set_is_function(is_function)

            elif self.found_void_type:
                self.reject_semantic("invalid type for variable, void")

            if not self.symbol_table.add_symbol(current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + current_symbol.identifier)

            if self.current_token == ["(", "OPERATORS"]:

                size = self.calculate_quadruple_size(type, [False, None])
                self.add_quadruple("func", identifier, type, size)

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
                array_info = self.var_declaration()
                size = self.calculate_quadruple_size(type, array_info)
                self.add_quadruple("alloc", size, "", identifier)

            self.parsing_main = False

        self.end()

    # var-declaration -> type-specifier ID ; | type-specifier ID [ NUM ] ; | type-specifier ID [ FLOAT ] ;
    def var_declaration(self):
        self.start()

        is_array = False
        size = 0

        if self.current_token == ['[', 'OPERATORS']:
            is_array = True
            self.match("OPERATORS", "[")
            size = self.integer()
            self.match("OPERATORS", "]")

        self.match("OPERATORS", ";")

        self.end()

        return [is_array, size]

    # function-declaration -> type-specifier ( params ) compound-statement
    def function_declaration(self):
        self.start()

        calling_function = self.last_token[0]

        self.match("OPERATORS", "(")
        self.params(calling_function)
        self.match("OPERATORS", ")")
        self.compound_statement(calling_function)

        if self.parsing_main is True and self.accepted is not False:
            self.main_function_exists = True

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
        match = self.match("NUMBER")
        self.end()

        return int(match)

    # any-number -> NUM | FLOAT
    def any_number(self):
        self.start()

        if self.current_token and self.current_token[1] == "NUMBER":
            self.match("NUMBER")
            any_number_type = "int"
        else:
            self.match("FLOAT")
            any_number_type = "float"

        self.end()

        return any_number_type

    # params -> void | params-list
    def params(self, calling_function):
        self.start()

        self.params_list(calling_function)

        self.end()

    # params-list -> params-list , param | param
    def params_list(self, calling_function):
        self.start()

        self.param(calling_function)
        while self.current_token == [",", "OPERATORS"] \
                and self.accepted is not False:
            self.match("OPERATORS", ",")
            self.param(calling_function)

        self.end()

    # param -> type-specifier ID | type-specifier ID [ NUM ]
    def param(self, calling_function):

        self.start()

        self.current_symbol = symbol_table.Symbol()
        self.current_symbol.set_scope(self.scope+1)
        self.current_symbol.set_parent(calling_function, self.scope)

        is_void = self.current_token == ["void", "KEYWORD"]
        type = self.current_token[0]
        self.type_specifier()

        is_void_with_identifier = is_void and \
            self.current_token and self.current_token[1] == "IDENTIFIER"

        if not is_void or is_void_with_identifier:
            identifier = self.current_token[0]
            self.current_symbol.set_identifier(identifier)

            if is_void_with_identifier and self.current_token[1] is "IDENTIFIER":
                self.reject_semantic("Void parameter cannot be named: " + str(self.calling_function) + ", " + self.current_token[0])
            self.match("IDENTIFIER")

            array_info = [False, None]
            if self.current_token == ['[', "OPERATORS"]:
                type += "[]"
                self.match('OPERATORS', '[')
                self.match('OPERATORS', ']')
                array_info = [True, 1]

            self.current_symbol.set_type(type)

            if not self.symbol_table.add_symbol(self.current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + identifier)

            size = self.calculate_quadruple_size(type, array_info)
            self.add_quadruple("alloc", size, "", identifier)

        self.current_symbol = None

        self.end()

    # compound-statement -> { local-declarations statement-list }
    def compound_statement(self, calling_function):
        self.start()
        self.match("OPERATORS", "{")
        self.scope += 1
        self.local_declarations()
        self.statement_list(calling_function)
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
            type = self.current_token[0]
            self.current_symbol.set_type(type)
            self.current_symbol.set_scope(self.scope)

            is_void = self.current_token and self.current_token == ["void", "KEYWORD"]

            self.type_specifier()

            if is_void and self.current_token and self.current_token[1] is "IDENTIFIER":
                self.reject_semantic("variables with type void are not permitted: " + str(self.current_token[0]))

            self.current_symbol.set_identifier(self.current_token[0])
            self.match("IDENTIFIER")
            array_info = self.var_declaration()

            if array_info[0]:
                self.current_symbol.set_type(type+"[]")

            if not self.symbol_table.add_symbol(self.current_symbol):
                self.reject_semantic("Symbol already exists in scope: " + self.current_symbol.identifier)

            self.current_symbol = None

        self.end()

    # statement-list -> statement-list statement | @
    def statement_list(self, calling_function):
        self.start()
        while self.current_token and self.current_token[0] != "}" and self.accepted is not False:
            self.statement(calling_function)

        self.end()

    # statement -> expression-statement | selection-statement | compound-statement
    #   | iteration-statement | return-statement | empty-statement
    def statement(self, calling_function):
        self.start()
        if self.current_token[0] == "if":
            self.selection_statement(calling_function)
        elif self.current_token[0] == "while":
            self.iteration_statement(calling_function)
        elif self.current_token[0] == "return":
            self.return_statement(calling_function)
        elif self.current_token[0] == "{":
            self.compound_statement(calling_function)
        elif self.current_token[0] == ";":
            self.empty_statement()
        else:
            self.expression_statement()

        self.end()

    # selection-statement -> if ( expression ) statement | if ( expression ) statement else statement
    def selection_statement(self, calling_function):
        self.start()
        self.match("KEYWORD", "if")
        self.match("OPERATORS", "(")
        self.expression()
        self.match("OPERATORS", ")")
        self.statement(calling_function)
        if self.current_token and self.current_token[0] == "else":
            self.match("KEYWORD", "else")
            self.statement(calling_function)

        self.end()

    # iteration-statement -> while ( expression ) statement
    def iteration_statement(self, calling_function):

        self.start()

        self.match("KEYWORD", "while")
        self.match("OPERATORS", "(")
        self.expression()
        self.match("OPERATORS", ")")
        self.statement(calling_function)

        self.end()

    # return-statement -> return expression ; | return ;
    def return_statement(self, calling_function):

        self.start()

        self.match("KEYWORD", "return")
        if self.current_token != [';', 'OPERATORS']:
            if self.parsing_void_function:
                self.reject_semantic("Void function should not have a return value.")
            else:
                calling_symbol = self.symbol_table.exists(calling_function, self.scope)

                calling_symbol_type = ""
                if not calling_symbol:
                    self.reject_semantic("unknown calling function detected: '" + calling_symbol + "'")
                else:
                    calling_symbol_type = calling_symbol.type

                if self.current_token and self.current_token[0] == "[" and calling_symbol_type.endwith("[]"):
                    calling_symbol_type = calling_symbol_type[:-2]

                expression_type = self.expression(calling_symbol_type)

                if not calling_symbol:
                    self.reject_semantic("function is undefined... eh?")
                elif calling_symbol.type != expression_type:
                    self.reject_semantic("return value is invalid type")

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
    def assignment_statement(self, assignment_statement_type):

        self.start()

        self.match("OPERATORS", "=")
        expression_type = self.expression(assignment_statement_type)

        if expression_type != assignment_statement_type:
            self.reject_semantic("attempted to assign a " + str(expression_type) + " to " + \
                                 str(assignment_statement_type) + " var")

        self.end()

        return assignment_statement_type

    # expression -> ID var assignment-expression | simple-expression
    def expression(self, expression_type=None):
        self.start()

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            active_symbol = self.symbol_table.exists(self.current_token[0], self.scope)

            active_symbol_type = ""
            if not active_symbol:
                self.reject_semantic("Unknown symbol encountered: '" + self.current_token[0] + "'")
            else:
                active_symbol_type = active_symbol.type

            if active_symbol:
                self.match("IDENTIFIER")

                if self.current_token == ["[", "OPERATORS"] and active_symbol_type.endswith("[]"):
                    active_symbol_type = active_symbol_type[:-2]

                if not expression_type:
                    expression_type = active_symbol_type
                    if self.current_token == ["[", "OPERATORS"] and expression_type.endswith("[]"):
                        expression_type = expression_type[:-2]
                elif expression_type != active_symbol_type:
                    self.reject_semantic("operand type mismatch in expression *")

                var_type = self.var(expression_type)
                if expression_type != var_type:
                    self.reject_semantic("operand type mismatch in expression **")

                if self.current_token and self.current_token[0] == "=":
                    assignment_type = self.assignment_statement(expression_type)

                    if expression_type != assignment_type:
                        self.reject_semantic("operand type mismatch in expression ***")

                else:
                    simple_expression_type = self.simple_expression(expression_type)

                    if expression_type != simple_expression_type:
                        self.reject_semantic("operand type mismatch in expression ***")
            else:
                self.reject_semantic("Undeclared identifier: " + self.current_token[0])
        else:
            simple_expression_type = self.simple_expression(expression_type)

            if not expression_type:
                expression_type = simple_expression_type
            elif expression_type != simple_expression_type:
                self.reject_semantic("operand type mismatch in expression ***")

        self.end()

        return expression_type

    # simple-expression -> additive-expression relational-expression
    def simple_expression(self, simple_expression_type=None):

        self.start()

        simple_expression_type = self.additive_expression(simple_expression_type)
        self.relational_expression(simple_expression_type)

        self.end()

        return simple_expression_type

    # relational-expression -> relational-operation additive expression relational-operation | @
    def relational_expression(self, relational_expression_type):

        self.start()
        while self.current_token and self.current_token[0] in ['<=', '<', '>', '>=', '==', '!='] \
                and self.accepted is not False:
            self.relational_operation()
            relational_expression_type = self.additive_expression(relational_expression_type)

        self.end()

        return relational_expression_type

    # additive-expression -> term | add-operation term additive-expression
    def additive_expression(self, additive_expression_type=None):

        self.start()

        term_type = self.term(additive_expression_type)
        if not additive_expression_type:
            additive_expression_type = term_type
        elif additive_expression_type != term_type:
            self.reject_semantic("operand type mismatch in additive expression *")

        while self.current_token and self.current_token[0] in ["+", "-"] \
                and self.accepted is not False:
            opcode = "add" if self.current_token[0] == "+" else "sub"
            self.add_operation()
            term_type = self.term(additive_expression_type)

            if term_type != additive_expression_type:
                self.reject_semantic("operand type mismatch in additive expression **")

        self.end()

        return additive_expression_type

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
    def term(self, term_type=None):

        self.start()

        factor_type = self.factor(term_type)
        if not term_type:
            term_type = factor_type
            if self.current_token == ["[", "OPERATORS"] and term_type.endswith("[]"):
                term_type = term_type[:-2]
        elif term_type != factor_type:
            self.reject_semantic("operand type mismatch in term *")

        while self.current_token and self.current_token[0] in ["*", "/"] \
                and self.accepted is not False:
            identifier = self.last_token[0]
            opcode = "times" if self.current_token[0] == "*" else "div"
            self.multiply_operation()

            size = self.calculate_quadruple_size(term_type, [False, None])
            self.add_quadruple(opcode, identifier, self.current_token[0], "_t"+str(len(self.temps)))
            self.temps.append(len(self.temps))

            factor_type = self.factor(term_type)
            if factor_type != term_type:
                self.reject_semantic("operand type mismatch in term **")

        self.end()

        return term_type

    # factor -> ( expression ) | call | var | NUM | FLOAT
    def factor(self, factor_type=None):
        self.start()

        if self.current_token == ["(", "OPERATORS"]:
            if self.last_token and self.last_token[1] == "IDENTIFIER":
                if not self.symbol_table.function_exists(self.last_token[0], self.scope):
                    self.reject_semantic("" + self.last_token[0] + " is not a function")

                self.calling_function = self.last_token[0]
                factor_type = self.call()
            else:
                self.match("OPERATORS", "(")
                factor_type = self.expression(factor_type)
                self.match("OPERATORS", ")")
        elif self.current_token and self.current_token[1] in ["NUMBER", "FLOAT"]:
            factor_type = self.any_number()
        else:
            factor_type = self.call_or_var(factor_type)

        self.end()

        return factor_type

    # call-or-var -> ID | call | var
    def call_or_var(self, call_or_var_type=None):
        self.start()

        self.calling_function = self.last_token[0]

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            var_type = self.symbol_table.load_type(self.current_token[0], self.scope)
            self.match("IDENTIFIER")

            if self.current_token and self.current_token[0] == "[":
                var_type = var_type[:-2]

            if not call_or_var_type:
                call_or_var_type = var_type
            elif call_or_var_type != var_type:
                self.reject_semantic("operand type mismatch in call_or_var *")

            self.calling_function = self.last_token[0]

        if self.current_token == ["(", "OPERATORS"]:
            call_type = self.call()
            if not call_or_var_type:
                call_or_var_type = call_type
            elif call_type != call_or_var_type:
                self.reject_semantic("operand type mismatch in call_or_var **")
        else:
            active_symbol = self.symbol_table.exists(self.current_token[0], self.scope)
            if active_symbol:
                var_type = self.var(active_symbol.type)
                if not call_or_var_type:
                    call_or_var_type = var_type
                elif call_or_var_type != var_type:
                    self.reject_semantic("operand type mismatch in call_or_var ***")

            else:
                var_type = self.var(call_or_var_type)
                if not call_or_var_type:
                    call_or_var_type = var_type
                elif call_or_var_type != var_type:
                    self.reject_semantic("operand type mismatch in call_or_var ****")

        self.calling_function = None

        self.end()

        return call_or_var_type

    # call -> ( args )
    def call(self):
        self.start()

        called_function = self.calling_function

        function_params = self.symbol_table.load_params(self.calling_function, self.scope)
        call_type = self.symbol_table.load_type(self.calling_function, self.scope)

        self.match("OPERATORS", "(")
        args_parsed = self.args()
        self.match("OPERATORS", ")")

        if len(args_parsed) != len(function_params):
            self.reject_semantic("Mismatched number of arguments for '" + str(called_function) + "'. Found " +
                                 str(len(args_parsed)) + ", Expected " + str(len(function_params)))

        # check if args parsed is same type as param
        else:
            for i in range(0, len(args_parsed)):
                if args_parsed[i] != function_params[i].type:
                    self.reject_semantic("Mismatched type of argument index " + str(i) + " for '" + str(called_function) + "'. Found " +
                                 str(args_parsed[i]) + ", Expected " + str(function_params[i].type))

        self.end()

        return call_type

    # var -> [ expression ] | @
    def var(self, var_type):

        self.start()

        if self.current_token and self.current_token[1] == "IDENTIFIER":
            self.match("IDENTIFIER")
            var_type = self.var(var_type)

        if self.last_token and self.last_token[1] == "IDENTIFIER" and self.current_token[0] != "(":
            if not self.symbol_table.var_exists(self.last_token[0], self.scope):
                self.reject_semantic("" + self.last_token[0] + " is a function, not a variable")

        if self.current_token == ["[", "OPERATORS"]:
            self.match("OPERATORS", "[")

            if var_type.endswith("[]"):
                # remove [], value was de-referenced
                var_type = var_type[:-2]

            array_index_type = self.expression("int") # hard code to an int - array index should be an int
            if array_index_type != "int":
                self.reject_semantic("array index type was not int, was " + array_index_type + " instead")
            self.match("OPERATORS", "]")

        self.end()

        return var_type

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
        if self.current_token is not None and self.current_token[1] == token_type:
            if token_value is not None:
                if self.current_token[0] == token_value:
                    if self.debug:
                        print("\t"*self.indentation + "Token matched (by value): " + str(self.current_token))
                    return_value = self.current_token[0]
                    self.next_token()
                    return return_value
            else:
                if self.debug:
                    print("\t"*self.indentation + "Token matched (by type): " + str(self.current_token))
                return_value = self.current_token[0]
                self.next_token()
                return return_value

        self.reject(token_type, token_value)

        return None

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

    # generate code
    def add_quadruple(self, opcode, operand1, operand2, result):
        self.quadruples.append([len(self.quadruples)+1, opcode, operand1, operand2, result])

    #calculate size of a new quadruple
    def calculate_quadruple_size(self, type, array_info):
        size = 0
        if type is not "void":
            size = 4
            if array_info[0] and array_info[1]:
                size *= array_info[1]

        return size

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

