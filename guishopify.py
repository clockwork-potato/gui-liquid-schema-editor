import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import json
import re

ctk.set_appearance_mode("System")  # Light/Dark/System
ctk.set_default_color_theme("blue")  # Color theme

shopify_schema_types = [
    "text", "image_picker", "html", "radio", "select",
    "checkbox", "number", "range", "color", "url", "textarea"
]

class LiquidSchemaEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Liquid Schema Editor")
        self.geometry("1000x600")

        self.current_file = None
        self.schema_data = None

        self.create_widgets()

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill='x', pady=10, padx=10)

        open_button = ctk.CTkButton(top_frame, text="Open Liquid File", command=self.open_file)
        open_button.pack(side='left', padx=10)

        save_button = ctk.CTkButton(top_frame, text="Save Changes", command=self.save_file)
        save_button.pack(side='right', padx=10)

        add_block_button = ctk.CTkButton(top_frame, text="Add Block", command=self.add_block_dialog)
        add_block_button.pack(side='left', padx=10)

        self.scrollable_frame = ctk.CTkFrame(self)
        self.scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')

        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def open_file(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("liquid files", "*.liquid"), ("all files", "*.*")))
        if filename:
            with open(filename, 'r') as file:
                content = file.read()
                schema_block = re.search(r'{%\s*schema\s*%}(.*?){%\s*endschema\s*%}', content, re.DOTALL)
                if schema_block:
                    schema_json = schema_block.group(1).strip()
                    try:
                        self.schema_data = json.loads(schema_json)
                        self.current_file = filename
                        self.load_schema()
                    except json.JSONDecodeError:
                        messagebox.showerror("Error", "Invalid JSON format in schema block.")
                else:
                    messagebox.showerror("Error", "No schema block found.")

    def save_file(self):
        if self.current_file and self.schema_data is not None:
            try:
                updated_schema = json.dumps(self.schema_data, indent=4)
                with open(self.current_file, 'w') as file:
                    file.write(updated_schema)
                messagebox.showinfo("Success", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def add_block_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Block")
        dialog.geometry("300x150")

        label = ctk.CTkLabel(dialog, text="Select Block Type:")
        label.pack(pady=10)

        block_type_var = tk.StringVar(dialog)
        block_type_dropdown = ctk.CTkOptionMenu(dialog, variable=block_type_var, values=shopify_schema_types)
        block_type_dropdown.pack()

        add_button = ctk.CTkButton(dialog, text="Add", command=lambda: self.add_block(block_type_var.get()))
        add_button.pack(pady=10)

    def add_block(self, block_type):
        if block_type and self.schema_data is not None:
            new_block = {'type': block_type, 'settings': []}
            self.schema_data['blocks'].append(new_block)
            self.load_schema()

    def load_schema(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        if self.schema_data and 'blocks' in self.schema_data:
            for block in self.schema_data['blocks']:
                block_frame = ctk.CTkFrame(self.frame)
                block_frame.pack(fill='x', expand=True, pady=2)

                block_type_label = ctk.CTkLabel(block_frame, text=f"Type: {block['type']}", width=20)
                block_type_label.pack(side='left', padx=10)

                if 'settings' in block:
                    for setting in block['settings']:
                        setting_frame = ctk.CTkFrame(block_frame)
                        setting_frame.pack(fill='x', expand=True, pady=2)

                        setting_label = ctk.CTkLabel(setting_frame, text=setting['id'])
                        setting_label.pack(side='left', padx=10)

                        setting_entry = ctk.CTkEntry(setting_frame)
                        setting_entry.insert(0, setting.get('default', ''))
                        setting_entry.pack(side='left', padx=10)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    app = LiquidSchemaEditor()
    app.mainloop()
