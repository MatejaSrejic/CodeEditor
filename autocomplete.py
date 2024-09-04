import tkinter as tk
import keyword
import builtins
from astree import ASTree
import re as regex

class Autocomplete:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.suggestions_listbox = None
        self.suggestion_window = tk.Toplevel()
        self.suggestion_window.wm_overrideredirect(True)
        self.suggestion_window_hidden = True
        self.suggestion_window.withdraw()
        self.suggestions_listbox = tk.Listbox(self.suggestion_window, selectmode=tk.SINGLE)
        self.suggestions_listbox.pack()

        self.keywords = keyword.kwlist
        self.variables = []
        self.functions = []
        self.default_functions = []

        for bulletin in dir(builtins):
            if bulletin[0].lower() == bulletin[0]:
                self.default_functions.append(bulletin)
            else:
                self.keywords.append(bulletin)

    def refresh_variables(self):
        text_widget_value = self.text_widget.get(1.0, "end")

        cursor_position = self.text_widget.index(tk.INSERT)
        line_number = cursor_position.split('.')[0]

        analyzer = ASTree(text_widget_value)
        analyzer.parse_code(int(line_number))
        self.variables = analyzer.retrieve_variables()
        self.functions = analyzer.retrieve_functions()
    
    def find_matches(self, current_word, word_list):
        return [word for word in word_list if word.lower().startswith(current_word.lower())]

    def on_key_release(self, event):
        exit_from = False
        try:
            if event.keysym in ['BackSpace', 'Delete', 'Escape', 'Return']:
                self.hide_suggestions()
                exit_from = True
            
            if event.keysym in ['Return', 'Space']:
                self.refresh_variables()
                exit_from = True
        except: pass
        
        if exit_from: return

        current_word = self.get_current_word()
        current_word = current_word.replace("	", "")
        if current_word:
            matches = self.find_matches(current_word, list(set(self.keywords + self.variables + self.functions + self.default_functions)))
            if current_word in matches: matches.remove(current_word)
            if matches:
                self.show_suggestions(list(set(matches)))
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()

    def get_current_word(self):
        cursor_position = self.text_widget.index(tk.INSERT)
        line_start = str(cursor_position.split('.')[0]) + ".0"
        line_text = self.text_widget.get(line_start, cursor_position)

        match = regex.search(r'\b(\w+)$', line_text)
    
        if match:
            return match.group(1)
        else:
            return ""

    def show_suggestions(self, matches):
        # potreban listbox i toplevel
        # alg: toplevel i listbox se kreiraju jedanput tokom __inic__, i samo se pomera toplevel
        if self.suggestion_window_hidden:
            self.suggestion_window.deiconify()
            self.suggestion_window_hidden = False
        
        x, y, _, _ = self.text_widget.bbox(tk.INSERT)
        x += self.text_widget.winfo_rootx()
        y += self.text_widget.winfo_rooty() + 20 
        self.suggestion_window.geometry(f"+{x}+{y}")

        self.suggestions_listbox.delete(0, "end")
        self.suggestions_listbox.insert("end", *matches)

        self.suggestions_listbox.bind("<Return>", self.insert_selected)
        self.suggestions_listbox.bind("<Double-Button-1>", self.insert_selected)

        self.text_widget.bind("<Up>", self.focus_listbox)
        self.text_widget.bind("<Down>", self.focus_listbox)

        self.text_widget.focus_set()


    def hide_suggestions(self, event=None):
        if not self.suggestion_window_hidden:
            self.suggestion_window.withdraw()
            self.suggestion_window_hidden = True
            
    def focus_listbox(self, event):
        self.suggestions_listbox.focus_set()
        self.navigate_suggestions(event)

    def navigate_suggestions(self, event):
        current_selection = self.suggestions_listbox.curselection()
        if event.keysym == "Down":
            if current_selection:
                next_index = (current_selection[0] + 1) % self.suggestions_listbox.size()
            else:
                next_index = -1
        elif event.keysym == "Up":
            if current_selection:
                next_index = (current_selection[0] - 1) % self.suggestions_listbox.size()
            else:
                next_index = self.suggestions_listbox.size() - 1

        self.suggestions_listbox.selection_clear(0, tk.END)  # Clear previous selection
        self.suggestions_listbox.selection_set(next_index)
        self.suggestions_listbox.see(next_index)  # Ensure the item is visible
        self.suggestions_listbox.activate(next_index)  # Set the active focus to this item

    def insert_selected(self, event):
        selected_word = self.suggestions_listbox.get(tk.ACTIVE)

        cursor_position = self.text_widget.index('insert')
        start_position = self.text_widget.search(r'\w*$', cursor_position, backwards=True, regexp=True)
        if start_position == '':
            start_position = cursor_position
        self.text_widget.delete(start_position, cursor_position)
        self.text_widget.insert(start_position, selected_word)
        
        self.text_widget.mark_set('insert', f"{start_position}+{len(selected_word)}c")
        self.hide_suggestions()

        # code snippets
        if (selected_word == "def"):
            # add function(): 
            # highlight function
            current_position = self.text_widget.index(tk.INSERT)
            self.text_widget.insert(current_position, ' function():\n    ')
            # Calculate start and end positions of 'function'
            snippet_start = f"{current_position} + 1c"  # Assuming a space before 'function'
            snippet_end = f"{snippet_start} + {len('function')}c"
            
            # Highlight the 'function' text
            self.text_widget.mark_set('insert', snippet_start)  # Move cursor to the start of 'function'
            self.text_widget.tag_add(tk.SEL, snippet_start, snippet_end)  # Select 'function'
            self.text_widget.see(tk.INSERT)  # Make sure the insertion point is visible
        elif (selected_word in self.functions or selected_word in self.default_functions):
            current_position = self.text_widget.index(tk.INSERT)
            self.text_widget.insert(current_position, '()')
            self.text_widget.mark_set('insert', f"{current_position}+{1}c")

        self.text_widget.focus_set()