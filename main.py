import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Frame, Listbox, Scrollbar
import subprocess
import keyword
import os
from autocomplete import Autocomplete
from syntax import SyntaxHighlighting

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")

        self.main_vertical_frame = Frame(root)
        self.main_vertical_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.horizontal_frame = Frame(self.main_vertical_frame)
        self.horizontal_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        self.file_list = Listbox(self.horizontal_frame)
        self.file_list.pack(side=tk.LEFT, fill='y')
        self.file_list.bind('<Double-Button-1>', self.load_selected_file)


        self.line_numbers = tk.Text(self.horizontal_frame, width=4, padx=4, takefocus=0,
                                    borderwidth=0, background="lightgray", state="disabled", font=("Consolas", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(self.horizontal_frame, wrap=tk.WORD, font=("Consolas", 12))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_area = scrolledtext.ScrolledText(self.main_vertical_frame, wrap=tk.WORD, height=10, font=("Consolas", 10))
        self.output_area.pack(side=tk.TOP, fill=tk.X)

        self.autocomplete = Autocomplete(self.text_area)
        self.syntax = SyntaxHighlighting(self.text_area)

        self.current_filepath = ""
        self.changed = False
        self.create_menu()
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.undo_stack = []
        self.redo_stack = []

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.line_numbers.config(yscrollcommand=self.on_scroll)
        self.text_area.bind("<MouseWheel>", self.on_mousewheel)
        self.text_area.bind("<Button-4>", self.on_mousewheel)
        self.text_area.bind("<Button-5>", self.on_mousewheel)
        self.text_area.bind("<Control-y>", self.redo)
        self.text_area.bind("<Control-z>", self.undo)
        self.text_area.bind("<KeyPress>", self.on_change)
        self.text_area.bind("<<Modified>>", self.syntax.on_text_change)

        self.root.bind_all("<Control-s>", self.save_file)
        self.root.bind_all("<Control-n>", self.new_file)
        self.root.bind_all("<Control-o>", self.open_file)

        self.populate_file_list()

    def unchange(self):
        self.changed = False

    def on_closing(self):
        if messagebox.askyesno("Quit", "Do you want to save your progress?"):
            self.save_file()
        self.root.quit()
    
    def on_change(self, event=None):
        non_typing_keys = {'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock'}
        if event.keysym not in non_typing_keys:
            self.changed = True

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

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_list(folder_path)

    def on_key_release(self, event=None):
        self.autocomplete.on_key_release(event)
        self.update_line_numbers(event)

    def open_file(self, event=None):
        if self.text_area.get(1.0, tk.END) != "" and self.changed:
            if messagebox.askyesno("Open file", "Do you want to save your progress?"):
                self.save_file()
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        self.current_filepath = file_path
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.highlight_syntax()
        self.root.after_idle(self.unchange)
        self.update_line_numbers()

    def save_file(self, event=None):
        if self.current_filepath == "":
            fp = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
            if fp:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END))
        else:
            with open(self.current_filepath, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
        self.unchange()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file = file_path
            if file_path not in self.file_list.get(0, tk.END):
                self.file_list.insert(tk.END, file_path)

    def new_file(self, event=None):
        if self.text_area.get(1.0, tk.END) != "" and self.changed:
            if messagebox.askyesno("New file", "Do you want to save your progress?"):
                self.save_file()
        self.current_filepath = ""
        self.text_area.delete(1.0, tk.END)
        self.root.after_idle(self.unchange)
        self.update_line_numbers()

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

    def undo(self, event=None):
        self.text_area.edit_undo()

    def redo(self, event=None):
        self.text_area.edit_redo()

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        num_lines = int(self.text_area.index('end-1c').split('.')[0])

        for i in range(1, num_lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        self.line_numbers.config(state=tk.DISABLED)

    def on_scroll(self, *args):
        self.line_numbers.yview("moveto", args[1])
        self.text_area.yview("moveto", args[1])

    def on_mousewheel(self, event):
        self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def populate_file_list(self, folder_path=None):
        self.file_list.delete(0, tk.END)
        folder_path = folder_path or '.'
        for file in os.listdir(folder_path):
            if file.endswith('.py'):
                self.file_list.insert(tk.END, os.path.join(folder_path, file))


if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
