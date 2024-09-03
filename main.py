import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Frame, Listbox
import subprocess
import keyword
import os
from autocomplete import Autocomplete

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")
        
        self.frame = Frame(root)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.file_list = Listbox(self.frame)
        self.file_list.pack(expand=True, fill='both')
        self.file_list.bind('<Double-Button-1>', self.load_selected_file)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 12))
        self.text_area.pack(expand=True, fill='both')

        self.autocomplete = Autocomplete(self.text_area)
        
        self.create_menu()
        
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("Consolas", 10))
        self.output_area.pack(expand=True, fill='both')

        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.undo_stack = []
        self.redo_stack = []

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.populate_file_list()

    def on_closing(self):
        if messagebox.askyesno("Quit", "Do you want to save your progress?"):
            self.save_file()
        self.root.quit()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        edit_menu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        
        run_menu = tk.Menu(menu)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

    def highlight_syntax(self, event=None):
        self.autocomplete.on_key_release(event)
        self.text_area.tag_remove("keyword", "1.0", tk.END)
        for kw in keyword.kwlist:
            start_index = '1.0'
            while True:
                start_index = self.text_area.search(kw, start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(kw)}c"
                self.text_area.tag_add("keyword", start_index, end_index)
                start_index = end_index
        self.text_area.tag_config("keyword", foreground="blue")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.highlight_syntax()
            self.file_list.insert(tk.END, file_path)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_list.insert(tk.END, "Untitled")

    def load_selected_file(self, event):
        selected_file = self.file_list.get(self.file_list.curselection())
        with open(selected_file, 'r') as file:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, file.read())
        self.highlight_syntax()

    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        with open("temp_code.py", "w") as temp_file:
            temp_file.write(code)
        result = subprocess.run(['python', 'temp_code.py'], capture_output=True, text=True)
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, result.stdout + result.stderr)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.text_area.get(1.0, tk.END))
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.undo_stack.pop())

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.text_area.get(1.0, tk.END))
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.redo_stack.pop())

    def populate_file_list(self):
        # Populate the file list with Python files from the current directory
        for file in os.listdir('.'):
            if file.endswith('.py'):
                self.file_list.insert(tk.END, file)

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()