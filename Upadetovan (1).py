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

        # Main Frame
        self.main_frame = Frame(root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # File List Frame
        self.file_frame = Frame(self.main_frame, width=250, bg="lightgray")
        self.file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # File Listbox and Scrollbar
        self.file_list = Listbox(self.file_frame, bg="white", selectbackground="lightblue", 
                                 font=("Consolas", 10), width=30, borderwidth=1, relief="solid")
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind('<Double-Button-1>', self.load_selected_file)

        self.scrollbar = Scrollbar(self.file_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=self.scrollbar.set)

        # Text Area Frame
        self.text_frame = Frame(self.main_frame)
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Code Editor Area
        self.text_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, font=("Consolas", 12))
        self.text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Output Area
        self.output_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, height=10, font=("Consolas", 10))
        self.output_area.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create Menu
        self.create_menu()
        
        # Bind Syntax Highlighting
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.undo_stack = []
        self.redo_stack = []

        # Protocol for closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_file = None
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
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
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

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_list(folder_path)

    def populate_file_list(self, folder_path=None):
        self.file_list.delete(0, tk.END)
        folder_path = folder_path or '.'
        for file in os.listdir(folder_path):
            if file.endswith('.py'):
                self.file_list.insert(tk.END, os.path.join(folder_path, file))

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
        self.current_file = selected_file

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file = file_path
            if file_path not in self.file_list.get(0, tk.END):
                self.file_list.insert(tk.END, file_path)


    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        with temp_file.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode())
            temp_file.close()
            result = subprocess.run(['python', temp_file.name], capture_output=True, text=True)
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

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
