import tkinter as tk
from tkinter import ttk, messagebox
import logging
from gui.utils import set_icon
from gui.constants import *

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent, auth_manager):
        super().__init__(parent)
        set_icon(self)
        self.title("Registrarse")
        self.geometry("600x800")
        self.minsize(500, 400)
        self.auth_manager = auth_manager
        self.center_window()
        self.configure(bg=BACKGROUND_COLOR)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Registro de Usuario", font=('Arial', 20, 'bold'), foreground=TEXT_COLOR, background=BACKGROUND_COLOR).grid(row=0, column=0, pady=30)

        form_frame = ttk.Frame(self, style='Transparent.TFrame')
        form_frame.grid(row=1, column=0, padx=70, pady=30, sticky="nsew")
        form_frame.columnconfigure(1, weight=1)

        fields = [
            ("Tipo de documento", ["TI", "CC", "CE", "PPT"]),
            ("Número de documento", None),
            ("Nombre", None),
            ("Correo", None),
            ("Contraseña", None),
            ("Confirmar Contraseña", None),
            ("Rol", ["usuario", "docentes", "directivos", "dueños"])
        ]

        self.entries = {}
        for i, (label, options) in enumerate(fields):
            ttk.Label(form_frame, text=label, style='Transparent.TLabel').grid(row=i, column=0, sticky="w", pady=15)
            if options:
                entry = ttk.Combobox(form_frame, values=options, style='TCombobox', width=40)
            else:
                entry = ttk.Entry(form_frame, style='TEntry', width=40)
                if "Contraseña" in label:
                    entry.config(show="*")
            entry.grid(row=i, column=1, sticky="ew", pady=15)
            self.entries[label] = entry

        ttk.Button(self, text="Registrarse", command=self.register, style='TButton').grid(row=2, column=0, pady=40)

        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style(self)
        style.configure('Transparent.TFrame', background=BACKGROUND_COLOR)
        style.configure('Transparent.TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=('Arial', 14))
        style.configure('TEntry', fieldbackground='white', font=('Arial', 14))
        style.configure('TCombobox', fieldbackground='white', font=('Arial', 14))
        style.configure('TButton', background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR, font=('Arial', 14))
        style.map('TButton', background=[('active', ACCENT_COLOR)])

    def center_window(self):
        pass
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    def register(self):
        data = {label: entry.get() for label, entry in self.entries.items()}
        logging.debug(f"Datos de registro: {data}")
        if data["Contraseña"] != data["Confirmar Contraseña"]:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        try:
            if self.auth_manager.register_user(
                    data["Tipo de documento"],
                    data["Número de documento"],
                    data["Nombre"],
                    data["Correo"],
                    data["Contraseña"],
                    data["Rol"]
            ):
                logging.debug("Usuario registrado correctamente")
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                self.destroy()
            else:
                logging.error("No se pudo registrar el usuario")
                messagebox.showerror("Error", "No se pudo registrar el usuario")
        except Exception as e:
            logging.exception("Error durante el registro")
            messagebox.showerror("Error", str(e))