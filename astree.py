import ast

class ASTree:
    def __init__(self, code):
        self.code = code
        self.variables = []

    def retrieve_variables(self):
        try:
            tree = ast.parse(self.code)
            self.visit(tree)
            print("Vars:", self.variables)
        except: pass
        return self.variables

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
            self.variables.append(node.name)
        
        for child in ast.iter_child_nodes(node):
            self.visit(child)