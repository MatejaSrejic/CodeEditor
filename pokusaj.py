import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import keyword

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")

        # Create the main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for line numbers
        self.line_numbers = tk.Text(self.frame, width=4, padx=4, takefocus=0,
                                    borderwidth=0, background="lightgray", state="disabled", font=("Consolas", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Create the ScrolledText widget with undo enabled
        self.text_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, undo=True, font=("Consolas", 12))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Synchronize the scrollbars
        # self.text_area.config(yscrollcommand=self.on_scroll)
        self.line_numbers.config(yscrollcommand=self.on_scroll)

        # Bind events to update line numbers and syntax highlighting
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.on_mousewheel)
        self.text_area.bind("<Button-4>", self.on_mousewheel)
        self.text_area.bind("<Button-5>", self.on_mousewheel)
        self.text_area.bind("<Control-y>", self.redo)
        self.text_area.bind("<Control-z>", self.undo)

        # Additional setup
        self.current_filepath = ""
        self.changed = False
        self.create_menu()

        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("Consolas", 10))
        self.output_area.pack(expand=True, fill='both')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.text_area.bind("<KeyPress>", self.on_change)

        # Keyboard shortcuts
        self.root.bind_all("<Control-s>", self.save_file)
        self.root.bind_all("<Control-n>", self.new_file)
        self.root.bind_all("<Control-o>", self.open_file)

    def unchange(self):
        self.changed = False

    def on_closing(self, event=None):
        if self.changed:
            if messagebox.askyesno("Quit", "Do you want to save your progress?"):
                self.save_file()
        self.root.quit()

    def on_change(self, event=None):
        # Exclude keys that don't type
        non_typing_keys = {'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock'}
        if event.keysym not in non_typing_keys:
            self.changed = True

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        edit_menu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        
        run_menu = tk.Menu(menu)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

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

    def new_file(self, event=None):
        if self.text_area.get(1.0, tk.END) != "" and self.changed:
            if messagebox.askyesno("New file", "Do you want to save your progress?"):
                self.save_file()
        self.current_filepath = ""
        self.text_area.delete(1.0, tk.END)
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

    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        with open("temp_code.py", "w", encoding='utf-8') as temp_file:
            temp_file.write(code)
        result = subprocess.run(['python', 'temp_code.py'], capture_output=True, text=True)
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, result.stdout + result.stderr)

    def undo(self, event=None):
        self.text_area.edit_undo()

    def redo(self, event=None):
        self.text_area.edit_redo()

    def update_line_numbers(self, event=None):
        # Update line numbers
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        # Get number of lines in text widget
        num_lines = int(self.text_area.index('end-1c').split('.')[0])

        # Add line numbers to the line_numbers widget
        for i in range(1, num_lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        self.line_numbers.config(state=tk.DISABLED)

    def on_scroll(self, *args):
        # print("ARGS")
        # print(*args)
        print(self.text_area.vbar.get())
        # Scroll the line_numbers widget when the text_area is scrolled
        self.line_numbers.yview("moveto", args[1])
        #self.line_numbers.see()

    # def on_scroll2(self, *args):
    #     print("ARGS")
    #     print(*args)
    #     # Scroll the line_numbers widget when the text_area is scrolled
        self.text_area.yview("moveto", args[1])




    def on_mousewheel(self, event):
        # Handle mouse wheel scrolling
        self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()




