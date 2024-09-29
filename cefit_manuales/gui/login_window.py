import tkinter as tk
from tkinter import ttk, messagebox
from .register_window import RegisterWindow
import logging
from gui.constants import *
from gui.images import get_login_background, get_icon

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, auth_manager):
        super().__init__(parent)
        self.parent = parent
        self.title("Iniciar sesión")
        self.geometry("1200x700")
        self.auth_manager = auth_manager
        self.iconbitmap(get_icon())
        self.center_window()

        # Cargar y configurar la imagen de fondo
        self.bg_photo = get_login_background((1200, 700))
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame para los widgets de login
        login_frame = tk.Frame(self, bg=BACKGROUND_COLOR, bd=2, relief=tk.SOLID)
        login_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=500)

        tk.Label(login_frame, text="Inicio de Sesión", font=('Arial', 24, 'bold'), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=30)

        tk.Label(login_frame, text="Tipo de Usuario:", font=('Arial', 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', padx=30)
        self.user_type = ttk.Combobox(login_frame, values=["usuario", "docentes", "directivos", "dueños"], width=30, font=('Arial', 12), state="readonly")
        self.user_type.pack(padx=30, pady=(0, 20))
        self.user_type.set("usuario")  # Valor por defecto

        tk.Label(login_frame, text="Email:", font=('Arial', 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', padx=30)
        self.email_entry = ttk.Entry(login_frame, width=32, font=('Arial', 12))
        self.email_entry.pack(padx=30, pady=(0, 20))

        tk.Label(login_frame, text="Contraseña:", font=('Arial', 14), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', padx=30)
        self.password_entry = ttk.Entry(login_frame, show="*", width=32, font=('Arial', 12))
        self.password_entry.pack(padx=30, pady=(0, 30))

        button_frame = tk.Frame(login_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=(0, 20))
        ttk.Button(button_frame, text="Iniciar Sesión", command=self.login, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 20))
        ttk.Button(button_frame, text="Registrarse", command=self.show_register_window, style='Custom.TButton').pack(side=tk.LEFT)

        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Custom.TButton', font=('Arial', 14), padding=10)
        style.map('Custom.TButton', background=[('active', ACCENT_COLOR)], foreground=[('active', 'white')])
        style.configure('TEntry', fieldbackground='white')
        style.configure('TCombobox', fieldbackground='white')

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()
        logging.debug(f"Intento de inicio de sesión para: {email}, tipo: {user_type}")

        try:
            if self.auth_manager.login(email, password, user_type):
                logging.debug("Inicio de sesión exitoso")
                self.destroy()
            else:
                logging.debug("Fallo en el inicio de sesión")
                messagebox.showerror("Error", "Correo, contraseña o tipo de usuario incorrectos")
        except Exception as e:
            logging.error(f"Error durante el inicio de sesión: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error durante el inicio de sesión: {str(e)}")

    def show_register_window(self):
        logging.debug("Abriendo ventana de registro")
        register_window = RegisterWindow(self, self.auth_manager)
        register_window.grab_set()
        self.wait_window(register_window)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')