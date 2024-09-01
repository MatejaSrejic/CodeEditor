import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import keyword

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")
        self.text_area = tk.Text(self.root, wrap='word', undo=True)
        self.text_area.pack(expand=1, fill='both')
        self.create_menu()
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<Tab>", self.indent_code)

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        run_menu = tk.Menu(menu)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))

    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        try:
            exec(code)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def highlight_syntax(self, event=None):
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

    def indent_code(self, event):
        self.text_area.insert(tk.INSERT, "    ")
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
