import ply.lex as lex
import ply.yacc as yacc
import json
import sys

# --- Семантичний аналізатор (Таблиця символів) ---
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
    def enter_scope(self):
        self.scopes.append({})
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
    def add(self, name, symbol_info):
        self.scopes[-1][name] = symbol_info
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

# --- 1. LEXER (Лексичний аналізатор) ---
keywords = {
    'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'return': 'RETURN',
    'int': 'TYPE_INT', 'void': 'TYPE_VOID', 'print': 'PRINT'
}
tokens = ('ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'ASSIGN', 'SEMI', 'COMMA', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE') + tuple(keywords.values())
t_PLUS, t_MINUS, t_TIMES, t_DIVIDE, t_MOD, t_ASSIGN, t_SEMI, t_COMMA, t_LPAREN, t_RPAREN, t_LBRACE, t_RBRACE, t_EQ, t_NE, t_LT, t_GT, t_LE, t_GE = r'\+', r'-', r'\*', r'/', r'%', r'=', r';', r',', r'\(', r'\)', r'\{', r'\}', r'==', r'!=', r'<', r'>', r'<=', r'>='
t_ignore = ' \t'
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value, 'ID')
    return t
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)
lexer = lex.lex()

# --- 2. PARSER (Синтаксичний аналізатор) ---
# ### MODIFIED ###: Повністю переписано згідно з правилами PLY (одна функція - одне правило)
symbol_table = SymbolTable()
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
)

def p_program(p):
    'program : function_list'
    p[0] = {'type': 'Program', 'body': p[1]}

def p_function_list_recursive(p):
    'function_list : function_list function'
    p[0] = p[1] + [p[2]]

def p_function_list_single(p):
    'function_list : function'
    p[0] = [p[1]]

def p_function(p):
    'function : type_specifier ID LPAREN param_list RPAREN LBRACE block_item_list RBRACE'
    symbol_table.add(p[2], {'type': 'function', 'returnType': p[1], 'params': p[4]})
    symbol_table.enter_scope()
    for param in p[4]:
        symbol_table.add(param['name'], {'type': param['dataType']})
    p[0] = {'type': 'FunctionDef', 'returnType': p[1], 'name': p[2], 'params': p[4], 'body': p[7]}
    symbol_table.exit_scope()

def p_type_specifier_int(p):
    'type_specifier : TYPE_INT'
    p[0] = p[1]

def p_type_specifier_void(p):
    'type_specifier : TYPE_VOID'
    p[0] = p[1]

def p_param_list_items(p):
    'param_list : param_list_items'
    p[0] = p[1]

def p_param_list_empty(p):
    'param_list : empty'
    p[0] = []

def p_param_list_items_recursive(p):
    'param_list_items : param_list_items COMMA param'
    p[0] = p[1] + [p[3]]

def p_param_list_items_single(p):
    'param_list_items : param'
    p[0] = [p[1]]

def p_param(p):
    'param : type_specifier ID'
    p[0] = {'type': 'Param', 'dataType': p[1], 'name': p[2]}

def p_block_item_list_recursive(p):
    'block_item_list : block_item_list statement'
    p[0] = p[1] + [p[2]]

def p_block_item_list_empty(p):
    'block_item_list : empty'
    p[0] = []

def p_statement(p):
    '''statement : expression_statement
                 | compound_statement
                 | selection_statement
                 | iteration_statement
                 | return_statement
                 | print_statement
                 | variable_decl'''
    p[0] = p[1]

def p_variable_decl_assign(p):
    'variable_decl : type_specifier ID ASSIGN expression SEMI'
    if p[2] in symbol_table.scopes[-1]:
        print(f"Semantic Error: Variable '{p[2]}' already declared in this scope (line {p.lineno(2)})")
        raise SystemExit
    symbol_table.add(p[2], {'type': p[1]})
    p[0] = {'type': 'VarDecl', 'dataType': p[1], 'name': p[2], 'init': p[4]}

def p_variable_decl_simple(p):
    'variable_decl : type_specifier ID SEMI'
    if p[2] in symbol_table.scopes[-1]:
        print(f"Semantic Error: Variable '{p[2]}' already declared in this scope (line {p.lineno(2)})")
        raise SystemExit
    symbol_table.add(p[2], {'type': p[1]})
    p[0] = {'type': 'VarDecl', 'dataType': p[1], 'name': p[2], 'init': None}

def p_expression_statement_expr(p):
    'expression_statement : expression SEMI'
    p[0] = p[1]

def p_expression_statement_empty(p):
    'expression_statement : SEMI'
    p[0] = None

def p_print_statement(p):
    'print_statement : PRINT LPAREN expression RPAREN SEMI'
    p[0] = {'type': 'Print', 'value': p[3]}

def p_return_statement_expr(p):
    'return_statement : RETURN expression SEMI'
    p[0] = {'type': 'Return', 'value': p[2]}

def p_return_statement_empty(p):
    'return_statement : RETURN SEMI'
    p[0] = {'type': 'Return', 'value': None}

def p_compound_statement(p):
    'compound_statement : LBRACE block_item_list RBRACE'
    symbol_table.enter_scope()
    p[0] = {'type': 'Block', 'body': p[2]}
    symbol_table.exit_scope()

def p_selection_statement_if(p):
    'selection_statement : IF LPAREN expression RPAREN statement'
    p[0] = {'type': 'If', 'test': p[3], 'consequent': p[5], 'alternate': None}

def p_selection_statement_if_else(p):
    'selection_statement : IF LPAREN expression RPAREN statement ELSE statement'
    p[0] = {'type': 'If', 'test': p[3], 'consequent': p[5], 'alternate': p[7]}

def p_iteration_statement(p):
    'iteration_statement : WHILE LPAREN expression RPAREN statement'
    p[0] = {'type': 'While', 'test': p[3], 'body': p[5]}

def p_expression_assign(p):
    'expression : ID ASSIGN expression'
    if not symbol_table.lookup(p[1]):
        print(f"Semantic Error: Assignment to undeclared variable '{p[1]}' (line {p.lineno(1)})")
        raise SystemExit
    p[0] = {'type': 'Assignment', 'target': p[1], 'value': p[3]}

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression'''
    p[0] = {'type': 'BinaryOp', 'op': p[2], 'left': p[1], 'right': p[3]}

def p_expression_call(p):
    'expression : ID LPAREN args RPAREN'
    symbol = symbol_table.lookup(p[1])
    if not symbol or symbol.get('type') != 'function':
        print(f"Semantic Error: Call to undeclared or non-function '{p[1]}' (line {p.lineno(1)})")
        raise SystemExit
    p[0] = {'type': 'Call', 'callee': p[1], 'args': p[3]}

def p_args_list(p):
    'args : arg_list'
    p[0] = p[1]

def p_args_empty(p):
    'args : empty'
    p[0] = []

def p_arg_list_recursive(p):
    'arg_list : arg_list COMMA expression'
    p[0] = p[1] + [p[3]]

def p_arg_list_single(p):
    'arg_list : expression'
    p[0] = [p[1]]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_id(p):
    'expression : ID'
    if not symbol_table.lookup(p[1]):
        print(f"Semantic Error: Use of undeclared variable '{p[1]}' (line {p.lineno(1)})")
        raise SystemExit
    p[0] = {'type': 'Identifier', 'name': p[1]}

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = {'type': 'Literal', 'value': p[1]}

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' (line {p.lineno})")
    else:
        print("Syntax error at EOF")
    raise SystemExit

parser = yacc.yacc()

# --- 3. GENERATOR CODE (Трансляція в Python) ---
# (Без змін)
def generate(node, indent=0):
    if node is None: return ""
    ind = "    " * indent
    ntype = node['type']
    if ntype == 'Program':
        code = "# Transpiled Python Code\nimport sys\n\n"
        for func in node['body']:
            code += generate(func, indent) + "\n"
        code += "\nif __name__ == '__main__':\n    main()"
        return code
    elif ntype == 'FunctionDef':
        params = ", ".join([p['name'] for p in node['params']])
        code = f"{ind}def {node['name']}({params}):\n"
        if not node['body']:
            code += f"{ind}    pass\n"
        else:
            for stmt in node['body']:
                code += generate(stmt, indent + 1)
        return code
    elif ntype == 'VarDecl':
        val = generate(node['init']) if node['init'] else "0"
        return f"{ind}{node['name']} = {val}\n"
    elif ntype == 'Assignment':
        return f"{ind}{node['target']} = {generate(node['value'])}\n"
    elif ntype == 'Return':
        return f"{ind}return {generate(node['value'])}\n"
    elif ntype == 'Print':
        return f"{ind}print({generate(node['value'])})\n"
    elif ntype == 'If':
        code = f"{ind}if {generate(node['test'])}:\n"
        code += generate(node['consequent'], indent + 1) if node['consequent']['type'] == 'Block' else ("    " + ind + generate(node['consequent']).strip() + "\n")
        if node['alternate']:
            code += f"{ind}else:\n"
            code += generate(node['alternate'], indent + 1) if node['alternate']['type'] == 'Block' else ("    " + ind + generate(node['alternate']).strip() + "\n")
        return code
    elif ntype == 'While':
        code = f"{ind}while {generate(node['test'])}:\n"
        code += generate(node['body'], indent + 1) if node['body']['type'] == 'Block' else ("    " + ind + generate(node['body']).strip() + "\n")
        return code
    elif ntype == 'Block':
        code = ""
        for stmt in node['body']:
            code += generate(stmt, indent)
        return code
    elif ntype == 'BinaryOp':
        return f"({generate(node['left'])} {node['op']} {generate(node['right'])})"
    elif ntype == 'Call':
        args = ", ".join([generate(a) for a in node['args']])
        return f"{node['callee']}({args})"
    elif ntype == 'Literal':
        return str(node['value'])
    elif ntype == 'Identifier':
        return str(node['name'])
    elif ntype == 'Call' and indent > 0:
        return f"{ind}{generate(node, 0)}\n"
    return ""

# --- ТЕСТУВАННЯ ---
code_input_correct = """
int main() {
    int x = 10;
    if (x > 5) {
        int y = 20;
        print(y);
    }
    print(x);
    return 0;
}
"""
code_input_wrong_undeclared = """
int main() {
    x = 5;
    return 0;
}
"""
code_input_wrong_scope = """
int main() {
    if (1) {
        int y = 10;
    }
    y = 20;
    return 0;
}
"""

def test_code(code, name):
    print(f"--- Testing: {name} ---")
    print(code)
    global symbol_table
    symbol_table = SymbolTable()
    try:
        ast = parser.parse(code, lexer=lexer.clone())
        if ast:
            print("Parsing successful. AST generated.")
            with open('ast.json', 'w') as f:
                json.dump(ast, f, indent=2)
            py_code = generate(ast)
            print("\n--- Generated Python ---")
            print(py_code)
            print("\n--- Execution Output ---")
            exec(py_code)
        else:
            print("Parsing failed, no AST generated.")
    except SystemExit:
        print(f"\n---> Test '{name}' correctly failed due to a semantic/syntax error.")
    print("-" * 25 + "\n")

print("--- Running Semantic Analysis Tests ---")
test_code(code_input_correct, "Correct Code")
test_code(code_input_wrong_undeclared, "Undeclared Variable Error")
test_code(code_input_wrong_scope, "Out of Scope Variable Error")
