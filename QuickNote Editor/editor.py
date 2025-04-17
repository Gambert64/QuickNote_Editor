import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class ModernEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("QuickNote")
        self.geometry("1200x800")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Set logo
        try:
            # Get the absolute path to the icons directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "icons", "logo.png")
            
            if os.path.exists(logo_path):
                # Load and resize the logo
                logo_image = Image.open(logo_path)
                # Resize to a reasonable size for the window icon
                logo_image = logo_image.resize((32, 32), Image.Resampling.LANCZOS)
                
                # Convert to ICO format for Windows
                logo_ico_path = os.path.join(current_dir, "icons", "logo.ico")
                logo_image.save(logo_ico_path, format="ICO")
                
                # Set the window icon
                self.iconbitmap(logo_ico_path)
                
                # Clean up the temporary ICO file
                try:
                    os.remove(logo_ico_path)
                except:
                    pass
            else:
                print(f"Logo file not found at: {logo_path}")
        except Exception as e:
            print(f"Could not load logo: {e}")

        # Create menu bar
        self.create_menu_bar()

        # Create main container
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Create add tab button frame
        button_frame = ctk.CTkFrame(main_container)
        button_frame.grid(row=0, column=1, sticky="ns", padx=5)

        # Create add tab button
        self.add_tab_button = ctk.CTkButton(
            button_frame, 
            text="+", 
            width=30, 
            height=30,
            command=self.create_new_tab
        )
        self.add_tab_button.pack(pady=5)

        # Create initial tab
        self.create_new_tab()

        # Bind keyboard shortcuts
        self.bind_shortcuts()

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.create_new_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu
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
        # Create frame for the tab
        tab_frame = ctk.CTkFrame(self.notebook)
        
        # Create text widget
        text_widget = tk.Text(tab_frame, wrap=tk.WORD, font=("Consolas", 12))
        text_widget.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Enable undo/redo with proper behavior
        text_widget.configure(undo=True, autoseparators=True)
        
        # Create close button
        close_button = ctk.CTkButton(
            tab_frame, 
            text="×", 
            width=20, 
            height=20,
            command=lambda: self.close_tab(tab_frame)
        )
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
        
        # Create context menu for text widget
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Undo", command=lambda: self.undo_action(text_widget))
        context_menu.add_command(label="Redo", command=lambda: self.redo_action(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=lambda: text_widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))
        context_menu.add_command(label="Select All", command=lambda: text_widget.tag_add("sel", "1.0", "end"))
        
        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)
        
        text_widget.bind("<Button-3>", show_context_menu)
        
        # Add tab to notebook with larger size
        self.notebook.add(tab_frame, text="Untitled")
        self.notebook.select(tab_frame)
        
        # Configure notebook style for larger tabs
        style = ttk.Style()
        style.configure("TNotebook", padding=[10, 5])  # Add padding around tabs
        style.configure("TNotebook.Tab", padding=[10, 5])  # Make tabs larger
        
        # Bind double-click event for tab name editing
        self.notebook.bind("<Double-1>", self.on_tab_double_click)

        # Track changes in the text widget
        def on_text_change(event):
            current_tab = self.notebook.select()
            tab_title = self.notebook.tab(current_tab, "text")
            if not tab_title.endswith("*"):
                self.notebook.tab(current_tab, text=tab_title + "*")
        
        text_widget.bind("<<Modified>>", on_text_change)
        text_widget.edit_modified(False)

        # Bind key events for proper undo/redo behavior
        def on_key_press(event):
            # Create a new undo/redo action for every key press
            text_widget.edit_separator()
            text_widget.edit_modified(False)
        
        text_widget.bind('<Key>', on_key_press)

    def on_tab_double_click(self, event):
        # Get the clicked tab
        tab_id = self.notebook.identify(event.x, event.y)
        if tab_id:
            # Create entry widget for editing
            entry = tk.Entry(self.notebook)
            entry.insert(0, self.notebook.tab(tab_id, "text").rstrip("*"))
            entry.pack(expand=True, fill="both")
            
            def on_entry_return(event):
                new_name = entry.get()
                self.notebook.tab(tab_id, text=new_name)
                entry.destroy()
            
            def on_entry_focus_out(event):
                entry.destroy()
            
            entry.bind("<Return>", on_entry_return)
            entry.bind("<FocusOut>", on_entry_focus_out)
            entry.focus_set()

    def close_tab(self, tab_frame):
        if self.notebook.index("end") > 1:  # Don't close if it's the last tab
            # Check if the tab has unsaved changes
            current_tab = self.notebook.select()
            tab_title = self.notebook.tab(current_tab, "text")
            
            if tab_title.endswith("*"):
                response = messagebox.askyesnocancel(
                    "Save Changes",
                    f"Do you want to save changes to {tab_title.rstrip('*')}?",
                    default=messagebox.YES
                )
                
                if response is None:  # Cancel
                    return
                elif response:  # Yes
                    self.save_file()
            
            self.notebook.forget(tab_frame)
        else:
            messagebox.showinfo("Info", "Cannot close the last tab")

    def get_current_text_widget(self):
        current_tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(current_tab)
        return tab_frame.winfo_children()[0]

    def open_file(self):
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
                
                # Update tab title without .txt extension
                filename = os.path.basename(file_path)
                if filename.endswith('.txt'):
                    filename = filename[:-4]
                self.notebook.tab(self.notebook.select(), text=filename)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        current_tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(current_tab)
        text_widget = tab_frame.winfo_children()[0]
        
        # Get current file path from tab title
        current_file = self.notebook.tab(current_tab, "text").rstrip("*")
        
        if current_file == "Untitled":
            self.save_file_as()
        else:
            try:
                with open(current_file, "w", encoding="utf-8") as file:
                    file.write(text_widget.get(1.0, tk.END))
                # Remove the * from the tab title if it exists
                if self.notebook.tab(current_tab, "text").endswith("*"):
                    self.notebook.tab(current_tab, text=current_file)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    text_widget = self.get_current_text_widget()
                    file.write(text_widget.get(1.0, tk.END))
                
                # Update tab title without .txt extension
                filename = os.path.basename(file_path)
                if filename.endswith('.txt'):
                    filename = filename[:-4]
                self.notebook.tab(self.notebook.select(), text=filename)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def undo_action(self, text_widget):
        try:
            text_widget.edit_undo()
            text_widget.edit_modified(False)
        except:
            pass

    def redo_action(self, text_widget):
        try:
            text_widget.edit_redo()
            text_widget.edit_modified(False)
        except:
            pass

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.create_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())
        self.bind("<Control-z>", lambda e: self.undo_action(self.get_current_text_widget()))
        self.bind("<Control-y>", lambda e: self.redo_action(self.get_current_text_widget()))
        self.bind("<Control-a>", lambda e: self.get_current_text_widget().tag_add("sel", "1.0", "end"))

if __name__ == "__main__":
    app = ModernEditor()
    app.mainloop() 