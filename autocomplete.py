import tkinter as tk
import keyword

class Autocomplete:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.suggestion_window = None
        self.suggestions_listbox = None

        print("Autocomplete init success")

        # Lista svih Python ključnih reči i promenljivih (početno prazno)
        self.keywords = keyword.kwlist
        print(self.keywords)
        self.variables = []

        # Povezivanje funkcije za detekciju unosa u text_area
        self.text_widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event):
        print("Detected key release")
        if event.keysym in ['BackSpace', 'Delete']:
            self.hide_suggestions()
            return  # Ne trigeruje autocomplete pri brisanju
        
        # Detekcija trenutne reči
        current_word = self.get_current_word()
        if current_word:
            # Traženje podudaranja u listi ključnih reči i promenljivih
            matches = self.find_matches(current_word, self.keywords + self.variables)
            print("Matches", matches, "for '"+current_word+"'")
            if current_word == matches[0]: 
                self.hide_suggestions()
                return  # Ne trigeruje autocomplete pri brisanju
            elif matches:
                self.show_suggestions(matches)
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()

    def get_current_word(self):
        cursor_position = self.text_widget.index(tk.INSERT)
        line_start = f"{cursor_position.split('.')[0]}.0"
        line_text = self.text_widget.get(line_start, cursor_position)

        # Razdvajanje reči
        words = line_text.split()
        if words:
            return words[-1]
        return ""

    def find_matches(self, current_word, word_list):
        matches = [word for word in word_list if word.startswith(current_word)]
        return matches

    def show_suggestions(self, matches):
        if self.suggestion_window:
            self.suggestion_window.destroy()

        # Kreiranje novog prozora za sugestije
        self.suggestion_window = tk.Toplevel()
        self.suggestion_window.wm_overrideredirect(True)

        # Pozicioniranje prozora ispod kursora
        x, y, _, _ = self.text_widget.bbox(tk.INSERT)
        x += self.text_widget.winfo_rootx()
        y += self.text_widget.winfo_rooty() + 20  # Pomeri malo ispod kursora
        self.suggestion_window.geometry(f"+{x}+{y}")

        # Kreiranje liste za prikazivanje sugestija
        self.suggestions_listbox = tk.Listbox(self.suggestion_window, selectmode=tk.SINGLE)

        for match in matches:
            self.suggestions_listbox.insert(tk.END, match)

        self.suggestions_listbox.pack()

        # Povezivanje selekcije sa događajem Enter ili Double-Click
        self.suggestions_listbox.bind("<Return>", self.insert_selected)
        self.suggestions_listbox.bind("<Double-Button-1>", self.insert_selected)

        # Praćenje strelica gore/dole
        self.suggestions_listbox.bind("<Up>", self.navigate_suggestions)
        self.suggestions_listbox.bind("<Down>", self.navigate_suggestions)
        self.suggestions_listbox.focus_set()

    def hide_suggestions(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

    def navigate_suggestions(self, event):
        current_selection = self.suggestions_listbox.curselection()
        if event.keysym == "Down":
            if current_selection:
                next_index = (current_selection[0] + 1) % self.suggestions_listbox.size()
            else:
                next_index = 0
            self.suggestions_listbox.select_set(next_index)
        elif event.keysym == "Up":
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