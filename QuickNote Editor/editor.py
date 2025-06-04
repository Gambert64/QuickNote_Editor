import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk
import os

class ModernEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.title("QuickNote")
        self.geometry("1200x800")

        # Make window grid grow when resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create menu bar on top
        self.create_menu_bar()

        # Main frame to hold notebook and buttons
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Create tab control (notebook) to hold tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Frame for add tab button
        button_frame = ctk.CTkFrame(main_container)
        button_frame.grid(row=0, column=1, sticky="ns", padx=5)

        # Button to add new tab
        self.add_tab_button = ctk.CTkButton(
            button_frame,
            text="+",
            width=30,
            height=30,
            command=self.create_new_tab
        )
        self.add_tab_button.pack(pady=5)

        # Create first tab when program starts
        self.create_new_tab()

        # Add keyboard shortcuts
        self.bind_shortcuts()

    def create_menu_bar(self):
        # Create menu with File and Edit menus
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu with new, open, save, save as, exit
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.create_new_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu with undo, redo, cut, copy, paste, select all
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.get_current_text_widget().edit_undo())
        edit_menu.add_command(label="Redo", command=lambda: self.get_current_text_widget().edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.get_current_text_widget().event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.get_current_text_widget().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.get_current_text_widget().event_generate("<<Paste>>"))
        edit_menu.add_command(label="Select All", command=lambda: self.get_current_text_widget().tag_add("sel", "1.0", "end"))

    def create_new_tab(self):
        # Make a new tab with a text box and close button
        tab_frame = ctk.CTkFrame(self.notebook)

        # Text box for typing
        text_widget = tk.Text(tab_frame, wrap=tk.WORD, font=("Consolas", 12))
        text_widget.pack(expand=True, fill="both", padx=5, pady=5)

        # Allow undo and redo in text box
        text_widget.configure(undo=True, autoseparators=True)

        # Button to close the tab
        close_button = ctk.CTkButton(
            tab_frame,
            text="×",
            width=20,
            height=20,
            command=lambda: self.close_tab(tab_frame)
        )
        # Put close button top right corner
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        # Create right-click menu with undo, redo, cut, copy, paste, select all
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Undo", command=lambda: self.undo_action(text_widget))
        context_menu.add_command(label="Redo", command=lambda: self.redo_action(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=lambda: text_widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))
        context_menu.add_command(label="Select All", command=lambda: text_widget.tag_add("sel", "1.0", "end"))

        # Show right-click menu when right click
        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)

        text_widget.bind("<Button-3>", show_context_menu)

        # Add tab to notebook and select it
        self.notebook.add(tab_frame, text="Untitled")
        self.notebook.select(tab_frame)

        # Make tabs bigger with more padding
        style = ttk.Style()
        style.configure("TNotebook", padding=[10, 5])
        style.configure("TNotebook.Tab", padding=[10, 5])

        # When text changes, add * to tab title to show unsaved changes
        def on_text_change(event):
            current_tab = self.notebook.select()
            tab_title = self.notebook.tab(current_tab, "text")
            if not tab_title.endswith("*"):
                self.notebook.tab(current_tab, text=tab_title + "*")

        text_widget.bind("<<Modified>>", on_text_change)
        text_widget.edit_modified(False)  # reset modified flag

        # Add undo separator for each key press to make undo easier
        text_widget.bind("<Key>", lambda event: text_widget.edit_separator())

    def close_tab(self, tab_frame):
        # Do not close last tab
        if self.notebook.index("end") > 1:
            current_tab = self.notebook.select()
            tab_title = self.notebook.tab(current_tab, "text")

            # Ask to save if tab has unsaved changes (*)
            if tab_title.endswith("*"):
                response = messagebox.askyesnocancel(
                    "Save Changes",
                    f"Do you want to save changes to {tab_title.rstrip('*')}?",
                    default=messagebox.YES
                )

                if response is None:  # cancel close
                    return
                elif response:  # save before close
                    self.save_file()

            # Remove tab from notebook
            self.notebook.forget(tab_frame)
        else:
            messagebox.showinfo("Info", "Cannot close the last tab")

    def get_current_text_widget(self):
        # Return text box from current tab
        current_tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(current_tab)
        return tab_frame.winfo_children()[0]

    def open_file(self):
        # Open a file and show content in a new tab
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                self.create_new_tab()
                text_widget = self.get_current_text_widget()
                text_widget.delete(1.0, tk.END)
                text_widget.insert(1.0, content)

                # Set tab title to file name without .txt
                filename = os.path.basename(file_path)
                if filename.endswith('.txt'):
                    filename = filename[:-4]
                self.notebook.tab(self.notebook.select(), text=filename)

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        # Save content of current tab to file
        current_tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(current_tab)
        text_widget = tab_frame.winfo_children()[0]

        # Get file name from tab title
        current_file = self.notebook.tab(current_tab, "text").rstrip("*")

        # If file is new, use Save As dialog
        if current_file == "Untitled":
            self.save_file_as()
        else:
            try:
                with open(current_file, "w", encoding="utf-8") as file:
                    file.write(text_widget.get(1.0, tk.END))
                # Remove * from tab title after saving
                if self.notebook.tab(current_tab, "text").endswith("*"):
                    self.notebook.tab(current_tab, text=current_file)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def save_file_as(self):
        # Save content to a new file name from dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    text_widget = self.get_current_text_widget()
                    file.write(text_widget.get(1.0, tk.END))

                # Update tab title with new file name without .txt
                filename = os.path.basename(file_path)
                if filename.endswith('.txt'):
                    filename = filename[:-4]
                self.notebook.tab(self.notebook.select(), text=filename)

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def undo_action(self, text_widget):
        # Undo last change
        try:
            text_widget.edit_undo()
            text_widget.edit_modified(False)
        except:
            pass

    def bind_shortcuts(self):
        # Keyboard shortcuts for new, open, save, undo, redo, select all
        self.bind("<Control-n>", lambda e: self.create_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())
        self.bind("<Control-z>", lambda e: self.undo_action(self.get_current_text_widget()))
        self.bind("<Control-y>", lambda e: self.redo_action(self.get_current_text_widget()))
        self.bind("<Control-a>", lambda e: self.get_current_text_widget().tag_add("sel", "1.0", "end"))

if __name__ == "__main__":
    # Start the app
    app = ModernEditor()
    app.mainloop()