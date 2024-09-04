import tkinter as tk
import ast
import re

class SyntaxHighlighting:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.dict = {"Module": "blue", "Interactive": "blue", "Expression": "blue", "FunctionDef": "indigo", "AsyncFunctionDef":"indigo", 
        "ClassDef": "indigo", "Return": "purple", "Delete": "blue", "Assign": "blue", "TypeAlias": "blue", "AugAssign": "blue", "AnnAssign": "blue", 
        "For": "blue", "AsyncFor": "blue", "While": "blue", "If": "blue", "With": "blue", "AsyncWith": "blue", "Match": "blue", "Raise": "blue", "Try": "blue", 
        "TryStar": "blue", "Assert": "blue", "Import": "purple", "ImportFrom": "purple", "Global": "blue", "Nonlocal": "blue", "Expr": "blue", "Pass": "blue", 
        "Break": "blue", "Continue": "blue", "BoolOp": "blue", "NamedExpr": "blue", "BinOp": "blue", "UnaryOp": "blue", "Lambda": "blue", "IfExp": "blue",
        "Dict": "blue", "Set": "blue", "ListComp": "blue", "SetComp": "blue", "DictComp": "blue", "GeneratorExp": "blue", "Await": "blue","Yield": "blue", 
        "YieldFrom": "blue", "Compare": "blue", "Call": "blue", "FormattedValue": "blue", "JoinedStr": "blue", "Constant": "green", "Attribute": "blue",
        "Subscript": "blue", "Starred": "blue", "List": "blue", "Tuple": "blue", "Slice": "blue", "Attributes": "blue", "Loas": "blue", "Store": "blue", "Del": "blue",
        "And": "blue", "Or": "blue", "add": "blue", "Sub": "blue", "Mult": "blue", "MatMult": "blue", "Div": "blue", "Mod": "blue", "Pow": "blue", "LShift": "blue", "RShift":  "blue",
        "BitOr": "blue", "BitXor": "blue", "BitAnd": "blue", "FloorDiv": "blue", "Invert": "blue", "Not": "blue", "UAdd": "blue", "USub": "blue", "Eq": "blue", "NotEq": "blue", 
        "Lt": "blue", "LtE": "blue", "Gt": "blue", "GtE": "blue", "Is": "blue", "IsNot": "blue", "In": "blue", "NotIn": "blue", "comprehension": "blue", "ExceptHandler": "blue",
        "arguments": "blue", "arg": "blue", "keyword": "blue", "alias": "blue", "withitem": "blue", "match_case": "blue", "MatchValue": "blue", "MatchSingleton": "blue", "MatchSequance": "blue", 
        "MatchMapping": "blue", "MatchCLass": "blue", "MatchStar": "blue", "MatchAs": "blue", "MatchOr": "blue","TypeIgnore": "blue", "TypeVar": "blue",
        "ParamSpec": "blue", "TypeVarTuple": "blue", "syntax_error": "red", "highlight_comment": "green", "highlight_string": "brown"}

        for key, value in self.dict.items():
            self.text_widget.tag_config(key, foreground=value)

        print("Init success")



    def highlight_syntax(self, code):
        # Highlight comments and strings using regex
        comment_pattern = r'#.*'
        string_pattern = r'(["\'])(?:\\.|[^\\])*?\1'

        for match in re.finditer(comment_pattern, code):
            start = match.start()
            end = match.end()
            start_index = self.text_widget.index(f"1.0+{start}c")
            end_index = self.text_widget.index(f"1.0+{end}c")
            self.text_widget.tag_add('highlight_comment', start_index, end_index)

        for match in re.finditer(string_pattern, code):
            start = match.start()
            end = match.end()
            start_index = self.text_widget.index(f"1.0+{start}c")
            end_index = self.text_widget.index(f"1.0+{end}c")
            self.text_widget.tag_add('highlight_string', start_index, end_index)


    def get_word_positions(self, node):
        positions = []

        # Recursive function to visit each node
        def visit(n):
            if hasattr(n, 'lineno'):
                start = (n.lineno, n.col_offset)
                end = (n.end_lineno, n.end_col_offset) if hasattr(n, 'end_col_offset') else (n.lineno, n.col_offset + len(n.id) if isinstance(n, ast.Name) else n.col_offset)
                positions.append((n.__class__.__name__, start, end))
            
            for child in ast.iter_child_nodes(n):
                visit(child)
        
        visit(node)
        return positions

    def on_text_change(self, event):
        code = self.text_widget.get("1.0", tk.END).strip()

        # Clear previous highlights
        self.text_widget.tag_remove('Name', '1.0', tk.END)
        self.text_widget.tag_remove('syntax_error', '1.0', tk.END)

        # Remove all highlights assocƒiated with tags in the dictionary
        for tag in self.dict.keys():
            self.text_widget.tag_remove(tag, '1.0', tk.END)

        self.highlight_syntax(code)

        try:
            parsed_ast = ast.parse(code)
            positions = self.get_word_positions(parsed_ast)

            for ast_type, start, end in positions:
                start_index = f"{start[0]}.{start[1]}"
                end_index = f"{end[0]}.{end[1]}"
                if ast_type == "Name":
                    self.text_widget.tag_add('Name', start_index, end_index)
                    self.text_widget.tag_config('Name', foreground="purple")
                elif ast_type in self.dict:
                    self.text_widget.tag_remove('Name', start_index, end_index)
                    self.text_widget.tag_add(ast_type, start_index, end_index)

        except SyntaxError as e:
            # Highlight the line where the syntax error occurred
            cursor_position = self.text_widget.index(tk.INSERT)
            current_line_number = cursor_position.split('.')[0]
            line_number = e.lineno

            if (int(line_number) != int(current_line_number)):
                start_index = f"{line_number}.0"
                end_index = f"{line_number}.end"
                self.text_widget.tag_remove('Name', start_index, end_index)
                self.text_widget.tag_add('syntax_error', start_index, end_index) 



        self.text_widget.edit_modified(False)