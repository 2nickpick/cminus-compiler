#
#
#   Lexical Analyzer
#   This module contains functions and objects for use by the Lexical Analyzer
#
#


class LexicalAnalyzer(object):

    # C- keywords are defined here
    keywords = [
        "else",
        "if",
        "int",
        "return",
        "void",
        "while",
        "float",
        "break",
        "continue"
    ]

    # C- operators and special symbols are defined here
    operators = [
        "+",
        "-",
        "*",
        "/",
        ";",
        ",",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}"
    ]

    # C- equality operators separated for simplified processing
    # These tokens may be longer than one character - typical operators can skip the extra processing
    extendable_operators = [
        "<",
        ">",
        "!",  # NOTE: The bang (!) operator is invalid by itself, this is handled in the processing of the token
        "=",
    ]

    def __init__(self):

        self.debug = False
        self.comment_nesting_level = 0
        self.tokens = []
        self.active_token = ""
        self.token_type = ""

    def process_file(self, file):
    
        #
        #   Process File for Tokens
        #
    
        for line in file.readlines():
            line = line.replace("\n", "").replace("\t", "").strip() + " "
    
            if len(line) <= 1:
                continue

            if self.debug:
                print("\nINPUT: " + line)
    
            #
            #   Begin Line-by-Line Processing
            #
            current_position_in_line = 0
            while current_position_in_line < len(line):
    
                char = line[current_position_in_line]
                token_complete = False
                self.token_type = ""
    
                # Determine a potential token type
                if char is "/":
                    self.token_type = "OPERATOR_OR_COMMENT"
    
                elif char is "*":
                    self.token_type = "OPERATOR_OR_END_COMMENT"
    
                elif char.isalpha():
                    self.token_type = "KEYWORD_OR_IDENTIFIER"
    
                elif char.isdigit():
                    self.token_type = "NUMBER_OR_FLOAT"
    
                elif char is " ":
                    self.token_type = "SPACE"
                    self.active_token = ""
    
                    token_complete = True
                    self.process_complete_token()
    
                    current_position_in_line += 1
    
                elif char in self.extendable_operators:
                    self.token_type = "OPERATORS"
    
                elif char in self.operators:
                    self.token_type = "OPERATORS"
    
                    self.active_token = char
                    self.process_complete_token()
    
                    current_position_in_line += 1
                    token_complete = True
    
                else:
                    self.token_type = "ERROR"
    
                self.active_token = char
    
                # If token is not a single-character token, let's begin collecting characters for the token
                while not token_complete:
    
                    # let's prep the next character
                    current_position_in_line += 1
    
                    if current_position_in_line >= len(line):
                        # if we've reached the end of the line, process the token as is
                        if self.token_type is "OPERATORS" and self.active_token is "!":
                            self.token_type = "ERROR"
    
                        token_complete = True
                        self.process_complete_token()
                        break
    
                    # Process the next character into the token
                    char = line[current_position_in_line]
    
                    if self.token_type is "OPERATOR_OR_COMMENT":
                        if char is "*":  # multi line comment
                            self.comment_nesting_level += 1
                            self.active_token += char
                            current_position_in_line += 1
                            self.token_type = "COMMENT"
                            token_complete = True
                        elif char is "/":  # single line comment
                            self.active_token += char
                            token_complete = True
                            current_position_in_line = len(line)
                            self.token_type = "COMMENT"
                        else:
                            self.token_type = "OPERATORS"
                            token_complete = True
    
                        # end of the line, pass the token on
                        if current_position_in_line + 1 >= len(line):
                            token_complete = True
    
                    elif self.token_type is "OPERATORS":
                        if char is "=":  # extended operator
                            self.active_token += char
                            current_position_in_line += 1
                            token_complete = True
                        elif self.active_token is "!":
                            self.token_type = "ERROR"
                            token_complete = True
                        else:
                            token_complete = True
    
                    elif self.token_type is "OPERATOR_OR_END_COMMENT":
    
                        if char is "/":  # end of multiline comment
                            if self.comment_nesting_level > 0:
                                self.comment_nesting_level -= 1
                                self.active_token = ""
                                current_position_in_line += 1
                            else:
                                self.token_type = "OPERATORS"
    
                            token_complete = True
    
                        else:
                            self.token_type = "OPERATORS"
                            token_complete = True
    
                        # end of the line, pass the token on
                        if current_position_in_line + 1 >= len(line):
                            token_complete = True
    
                    elif self.token_type is "KEYWORD_OR_IDENTIFIER":
                        if char.isalpha():  # string is still being built
                            self.active_token += char
                        else:  # this is the end of the string
                            token_complete = True
    
                        # end of the line, pass the token on
                        if current_position_in_line + 1 >= len(line):
                            token_complete = True
    
                    elif self.token_type in ["NUMBER_OR_FLOAT", "NUMBER", "FLOAT"]:
                        if char.isdigit():
                            self.active_token += char
                        elif char is "E":
                            if 'E' in self.active_token:
                                self.active_token += char
                                self.token_type = "ERROR"
                            else:
                                self.active_token += char
                                self.token_type = "FLOAT"
                        elif char is ".":
                            if '.' in self.active_token:
                                self.active_token += char
                                self.token_type = "ERROR"
                            else:
                                self.active_token += char
                                self.token_type = "FLOAT"
                        elif char in ["+", "-"]:
                            if '+' in self.active_token or '-' in self.active_token:
                                self.active_token += char
                                self.token_type = "ERROR"
                            else:
                                self.active_token += char
                                self.token_type = "FLOAT"
                        else:  # this is the end of the string
                            token_complete = True
    
                        if token_complete and self.token_type is not "FLOAT":
                            self.token_type = "NUMBER"
    
                    elif self.token_type is "ERROR":
                        if char not in [" "]:
                            self.active_token += char
                        else:
                            token_complete = True
    
                    else:
                        token_complete = True
    
                    # process a completed token
                    if token_complete:
                        self.process_complete_token()

        return self.get_tokens()

    # Add a token to the collection to be passed to the parser
    def process_complete_token(self):
        self.active_token = self.active_token.strip()

        append_token = False

        if self.active_token is not "" and self.comment_nesting_level is 0:
            if self.token_type is "OPERATOR_OR_END_COMMENT":
                if self.active_token is "*":
                    self.token_type = "OPERATORS"
                    append_token = True
                else:
                    self.token_type = "COMMENT"

            elif self.token_type in ["KEYWORD_OR_IDENTIFIER"]:
                append_token = True
                if self.active_token in self.keywords:
                    self.token_type = "KEYWORD"
                else:
                    self.token_type = "IDENTIFIER"

            elif self.token_type not in ["COMMENT", "SPACE"]:
                append_token = True

        if append_token:
            self.tokens.append([self.active_token, self.token_type])

            tabs = 2
            if self.token_type in ["IDENTIFIER"]:
                tabs = 1
            elif self.token_type in ["FLOAT", "ERROR"]:
                tabs = 3

            if self.debug:
                print("[" + self.token_type + "]" + ("\t" * tabs) + self.active_token)

        self.active_token = ""

    def get_tokens(self):
        return self.tokens
