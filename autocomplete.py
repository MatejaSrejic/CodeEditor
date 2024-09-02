import tkinter as tk
import keyword
import builtins

class Autocomplete:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.suggestion_window = None
        self.suggestions_listbox = None

        print("Autocomplete initialized")

        self.keywords = keyword.kwlist + dir(builtins)
        self.keywords = list(set(self.keywords)) # izbrisi duplikate
        print(self.keywords)
        
        self.variables = []
    
    def find_matches(self, current_word, word_list):
        return [word for word in word_list if word.startswith(current_word)]

    def on_key_release(self, event):
        if event.keysym in ['BackSpace', 'Delete']:
            self.hide_suggestions()
            return

        print("on_key_release triggered")

        current_word = self.get_current_word()
        if current_word:
            matches = self.find_matches(current_word, self.keywords + self.variables)
            if current_word in matches: matches.remove(current_word)
            if matches:
                self.show_suggestions(matches)
                print("For word", current_word, "found", matches)
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()

    def get_current_word(self):
        cursor_position = self.text_widget.index(tk.INSERT)
        line_start = str(cursor_position.split('.')[0]) + ".0"
        line_text = self.text_widget.get(line_start, cursor_position)

        words = line_text.split(" ")
        if words:
            return words[-1]
        return ""

    def show_suggestions(self, matches):
        if self.suggestion_window:
            self.suggestion_window.destroy()

        self.suggestion_window = tk.Toplevel()
        self.suggestion_window.wm_overrideredirect(True)

        try:
            x, y, _, _ = self.text_widget.bbox(tk.INSERT)
            x += self.text_widget.winfo_rootx()
            y += self.text_widget.winfo_rooty() + 20 
            self.suggestion_window.geometry(f"+{x}+{y}")
        except:
            self.hide_suggestions()
            return

        self.suggestions_listbox = tk.Listbox(self.suggestion_window, selectmode=tk.SINGLE)

        for match in matches:
            self.suggestions_listbox.insert(tk.END, match)

        self.suggestions_listbox.pack()

        self.suggestions_listbox.bind("<Return>", self.insert_selected)
        self.suggestions_listbox.bind("<Double-Button-1>", self.insert_selected)

        self.text_widget.bind("<Up>", self.focus_listbox)
        self.text_widget.bind("<Down>", self.focus_listbox)

        self.text_widget.focus_set()

    def hide_suggestions(self):
        if self.suggestion_window:
            #self.suggestion_window.destroy()
            self.suggestion_window.withdraw()
            self.suggestion_window = None

    def focus_listbox(self, event):
        print("Detect ", event)
        self.suggestions_listbox.focus_set()
        self.navigate_suggestions(event)

    def navigate_suggestions(self, event):
        current_selection = self.suggestions_listbox.curselection()
        if event.keysym == "Down":
            print("Autocomplete down")
            if current_selection:
                next_index = (current_selection[0] + 1) % self.suggestions_listbox.size()
            else:
                next_index = 0
            self.suggestions_listbox.select_set(next_index)
        elif event.keysym == "Up":
            print("Autocomplete u")
            if current_selection:
                next_index = (current_selection[0] - 1) % self.suggestions_listbox.size()
            else:
                next_index = self.suggestions_listbox.size() - 1
            self.suggestions_listbox.select_set(next_index)

    def insert_selected(self, event):
        selected_word = self.suggestions_listbox.get(tk.ACTIVE)
        current_word = self.get_current_word()
        self.text_widget.insert(tk.INSERT, selected_word[len(current_word):])
        self.hide_suggestions()

        self.text_widget.focus_set()

    def add_variable(self, variable_name):
        if variable_name not in self.variables:
            self.variables.append(variable_name)