import ast
import tkinter as tk

class ASTree:
    def __init__(self, code):
        self.code = code
        self.variables = []
        self.functions = []

    def retrieve_variables(self):
        return self.variables
    
    def retrieve_functions(self):
        return self.functions
    

    def parse_code(self, current_line_number):
        lines = self.code.splitlines()
        lines_to_parse = lines[:current_line_number - 1] + lines[current_line_number:]

        code_to_parse = '\n'.join(lines_to_parse)

        try:
            tree = ast.parse(code_to_parse)
            self.visit(tree)
        except: pass

    def visit(self, node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.variables.append(target.id)
                elif isinstance(target, ast.Tuple):
                    for element in target.elts:
                        if isinstance(element, ast.Name):
                            self.variables.append(element.id)
        elif isinstance(node, ast.FunctionDef):
            self.functions.append(node.name)
        
        for child in ast.iter_child_nodes(node):
            self.visit(child)