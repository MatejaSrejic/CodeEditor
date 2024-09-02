import tkinter as tk
import keyword
import builtins
from astree import ASTree

class Autocomplete:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.suggestion_window = None
        self.suggestions_listbox = None

        self.keywords = keyword.kwlist + dir(builtins)
        self.keywords = list(set(self.keywords)) # izbrisi duplikate
        
        self.variables = []

    def refresh_variables(self):
        text_widget_value = self.text_widget.get(1.0, "end")
        analyzer = ASTree(text_widget_value)
        self.keywords = keyword.kwlist + dir(builtins)
        self.keywords += analyzer.retrieve_variables()
    
    def find_matches(self, current_word, word_list):
        return [word for word in word_list if word.startswith(current_word)]

    def on_key_release(self, event):
        if event.keysym in ['BackSpace', 'Delete', 'Escape']:
            self.hide_suggestions()
            return
        
        if event.keysym in ['Return', 'Space']:
            self.refresh_variables()
            return

        print("on_key_release triggered")

        current_word = self.get_current_word()
        current_word = current_word.replace("	", "")
        if current_word:
            matches = self.find_matches(current_word, self.keywords + self.variables)
            if current_word in matches: matches.remove(current_word)
            if matches:
                print("Trigger for release ", event)
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
        if self.suggestions_listbox:
            self.suggestions_listbox.destroy()

        if not self.suggestion_window:
            print("Pravim novi window!")
            self.suggestion_window = tk.Toplevel()
            self.suggestion_window.wm_overrideredirect(True)
            #self.suggestion_window.wm_attributes('-type', 'splash')
        else:
            print("Vec postoji, otkrivam ga!")
            self.suggestion_window.deiconify()

        try:
            x, y, _, _ = self.text_widget.bbox(tk.INSERT)
            x += self.text_widget.winfo_rootx()
            y += self.text_widget.winfo_rooty() + 20 
            self.suggestion_window.geometry(f"+{x}+{y}")
        except:
            self.hide_suggestions()
            return

        self.suggestions_listbox = tk.Listbox(self.suggestion_window, selectmode=tk.SINGLE)
        self.suggestions_listbox.pack()

        for match in matches:
            self.suggestions_listbox.insert(tk.END, match)

        print("Updated content of listbox", self.suggestions_listbox.get(0, "end"))

        #self.suggestions_listbox.exportselection = False   

        #self.suggestions_listbox.pack() MOZDA POSLE INSERT?

        self.suggestions_listbox.bind("<Return>", self.insert_selected)
        self.suggestions_listbox.bind("<Double-Button-1>", self.insert_selected)

        self.text_widget.bind("<Up>", self.focus_listbox)
        self.text_widget.bind("<Down>", self.focus_listbox)

        self.text_widget.focus_set()

    def hide_suggestions(self, event=None):
        if self.suggestion_window:
            #self.suggestion_window.destroy()
            self.suggestion_window.withdraw()
            self.suggestion_window = None
           #self.suggestions_listbox.pack_forget()
            self.suggestions_listbox.destroy()
            
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
        current_word = self.get_current_word().replace("	", "")
        print("Current word =", current_word)
        self.text_widget.insert(tk.INSERT, selected_word[len(current_word):])
        print("Inserting", selected_word[len(current_word):])
        self.hide_suggestions()

        self.text_widget.focus_set()

    def add_variable(self, variable_name):
        if variable_name not in self.variables:
            self.variables.append(variable_name)