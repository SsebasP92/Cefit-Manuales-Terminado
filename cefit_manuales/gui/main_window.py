import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import PyPDF2
from PIL import Image, ImageTk
import os
import shutil
import logging
from .forms import create_form
from .data_display import create_data_tree, update_data_tree
from .login_window import LoginWindow
from .register_window import RegisterWindow
from utils.auth_manager import AuthManager
import config
import fitz
import io
from gui.utils import set_icon
from gui.constants import *
def generate_preview(file_path):
    try:
        doc = fitz.open(file_path)
        first_page = doc.load_page(0)
        pix = first_page.get_pixmap()
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail((200, 200))
        return img
    except Exception as e:
        logging.error(f"Error al generar la vista previa: {str(e)}")
        return None
class MainWindow(tk.Toplevel):
    def __init__(self, parent, db_connector):
        super().__init__(parent)
        self.parent = parent
        self.title("Sistema de Manuales de Mantenimiento CEFIT")
        self.geometry("850x800")
        self.minsize(800, 80|0)
        self.configure(bg=BACKGROUND_COLOR)
        set_icon(self)
        self.db_connector = db_connector
        self.auth_manager = AuthManager(db_connector)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Estilos generales
        self.style.configure('MainWindow.TFrame', background=BACKGROUND_COLOR)
        self.style.configure('TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=('Arial', 12))
        self.style.configure('TButton', background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR, font=('Arial', 12))
        self.style.map('TButton', background=[('active', ACCENT_COLOR)])
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 12))
        self.style.configure('TCombobox', fieldbackground='white', font=('Arial', 12))

        # Estilos para Treeview
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground=TEXT_COLOR,
                             font=('Arial', 11))
        self.style.configure('Treeview.Heading', background=BUTTON_COLOR, foreground=TEXT_COLOR,
                             font=('Arial', 12, 'bold'))

        # Estilos para Notebook (pestañas)
        self.style.configure('TNotebook', background=BACKGROUND_COLOR)
        self.style.configure('TNotebook.Tab', background=BUTTON_COLOR, foreground=TEXT_COLOR, padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', ACCENT_COLOR)], foreground=[('selected', 'white')])

        # Estilos transparentes
        self.style.configure('Transparent.TFrame', background=BACKGROUND_COLOR)
        self.style.configure('Transparent.TLabelframe', background=BACKGROUND_COLOR, labeloutside=True)
        self.style.configure('Transparent.TLabelframe.Label', background=BACKGROUND_COLOR, foreground=TEXT_COLOR,
                             font=('Arial', 12, 'bold'))
        logging.debug("Iniciando MainWindow")
        self.center_window(self)
        self.withdraw()
        self.show_login_window()
    def show_login_window(self):
        logging.debug("Mostrando ventana de login")
        login_window = LoginWindow(self.parent, self.auth_manager)
        self.wait_window(login_window)
        if self.auth_manager.get_current_user():
            logging.debug("Login exitoso, configurando interfaz principal")
            self.setup_main_interface()
            self.deiconify()
        else:
            logging.debug("Login fallido o cancelado, cerrando aplicación")
            self.on_closing()
    def setup_main_interface(self):
        logging.debug("Configurando la interfaz principal")
        for widget in self.winfo_children():
            widget.destroy()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text='Manuales de Mantenimiento')
        self.setup_manual_tab()
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text='Gestión de Datos')
        self.setup_data_tab()
        self.create_menu()

        style = ttk.Style()
        style.configure("TLabel", font=('Arial', 12))
        style.configure("TButton", font=('Arial', 12))
        style.configure("Treeview", font=('Arial', 11))
        style.configure("TEntry", font=('Arial', 11))

        logging.debug("Interfaz principal configurada")

    def setup_manual_tab(self):
        self.manual_tab.configure(style='MainWindow.TFrame')
        self.manual_tab.columnconfigure(1, weight=3)
        self.manual_tab.rowconfigure(1, weight=1)

        ttk.Label(self.manual_tab, text="Manuales de Mantenimiento", font=('Arial', 18, 'bold'), foreground=TEXT_COLOR).grid(row=0, column=0, columnspan=2, pady=20, sticky='w', padx=20)

        # Frame principal que contiene la lista y la vista previa
        main_frame = ttk.Frame(self.manual_tab, style='Main.TFrame')
        main_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=20, pady=10)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        # Frame izquierdo para la lista y botones
        left_frame = ttk.Frame(main_frame, style='Main.TFrame')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # Lista de manuales existentes con scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=0, column=0, sticky='nsew')
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.manuals_listbox = tk.Listbox(list_frame, font=('Arial', 14), width=30, bg='white', fg=TEXT_COLOR)
        self.manuals_listbox.grid(row=0, column=0, sticky='nsew')
        self.manuals_listbox.bind('<<ListboxSelect>>', self.on_manual_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.manuals_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.manuals_listbox.configure(yscrollcommand=scrollbar.set)

        # Botones para ver, subir y eliminar manuales
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        button_frame.columnconfigure((0, 1, 2), weight=1)

        button_style = ttk.Style()
        button_style.configure('Large.TButton', font=('Arial', 12), padding=10)
        button_style.map('Large.TButton', background=[('active', ACCENT_COLOR)])
        ttk.Button(button_frame, text="Ver Manual", command=self.view_manual, style='Large.TButton').grid(row=0,
                                                                                                          column=0,
                                                                                                          sticky='ew',
                                                                                                          padx=2,
                                                                                                          pady=2)
        if self.auth_manager.check_permission('dueños'):
            ttk.Button(button_frame, text="Subir Manual", command=self.upload_manual, style='Large.TButton').grid(row=0,
                                                                                                                  column=1,
                                                                                                                  sticky='ew',
                                                                                                                  padx=2,
                                                                                                                  pady=2)
            ttk.Button(button_frame, text="Eliminar Manual", command=self.delete_manual, style='Large.TButton').grid(
                row=0, column=2, sticky='ew', padx=2, pady=2)

        # Frame derecho para la vista previa y descripción
        right_frame = ttk.Frame(main_frame, style='Main.TFrame')
        right_frame.grid(row=0, column=1, sticky='nsew')
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=3)
        right_frame.rowconfigure(1, weight=1)

        # Frame para la vista previa
        preview_frame = ttk.Frame(right_frame, relief='groove', borderwidth=2, style='Main.TFrame')
        preview_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.grid(row=0, column=0, sticky='nsew')
        self.preview_label.configure(anchor='center')  # Centra la imagen

        # Frame para la descripción
        description_frame = ttk.Frame(right_frame)
        description_frame.grid(row=1, column=0, sticky='nsew')
        description_frame.columnconfigure(0, weight=1)
        description_frame.rowconfigure(1, weight=1)

        ttk.Label(description_frame, text="Descripción del Manual:", font=('Arial', 14, 'bold')).grid(row=0, column=0,
                                                                                                      sticky='w',
                                                                                                      pady=(0, 5))
        self.description_text = tk.Text(description_frame, wrap='word', font=('Arial', 12), height=8, bg='white',
                                        fg='#333333')
        self.description_text.grid(row=1, column=0, sticky='nsew', pady=(0, 10))

        # Botones para editar y guardar la descripción
        button_frame = ttk.Frame(description_frame)
        button_frame.grid(row=2, column=0, sticky='ew')
        button_frame.columnconfigure((0, 1), weight=1)

        self.edit_button = ttk.Button(button_frame, text="Editar Descripción", command=self.toggle_edit_description,
                                      style='Large.TButton')
        self.edit_button.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        self.save_button = ttk.Button(button_frame, text="Guardar Descripción", command=self.save_description,
                                      style='Large.TButton')
        self.save_button.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        self.save_button.config(state='disabled')

        # Inicialmente, deshabilitar la edición de la descripción
        self.description_text.config(state='disabled')

        # Cargar la lista de manuales existentes
        self.load_manuals_list()

    def setup_data_tab(self):
        self.data_tab.configure(style='MainWindow.TFrame')
        self.data_tab.columnconfigure(0, weight=1)
        self.data_tab.rowconfigure(1, weight=1)

        ttk.Label(self.data_tab, text="Gestión de Datos", font=('Arial', 18, 'bold'), foreground=TEXT_COLOR).grid(row=0,
                                                                                                                  column=0,
                                                                                                                  pady=20,
                                                                                                                  sticky='w',
                                                                                                                  padx=20)

        ttk.Button(self.data_tab, text="Acceder a Gestión de Datos", command=self.show_data_management_login,
                   style='TButton').grid(row=1, column=0, pady=50)
    def show_data_management_login(self):
        current_user = self.auth_manager.get_current_user()
        if current_user and self.auth_manager.check_permission('dueños'):
            # Si el usuario es dueño, mostrar directamente la gestión de datos
            self.show_data_management()
        else:
            # Si el usuario no es dueño, mostrar mensaje de error
            messagebox.showerror("Error de Permisos",
                                 "No tienes los permisos necesarios para acceder a la gestión de datos. Esta función está reservada para usuarios con rol de dueño.")

    def show_data_management(self):
        data_window = tk.Toplevel(self)
        data_window.configure(bg=BACKGROUND_COLOR)
        set_icon(data_window)
        data_window.title("Gestión de Datos")
        data_window.geometry("1800x1000")
        self.center_window(data_window)
        data_window.protocol("WM_DELETE_WINDOW", lambda: self.close_data_management(data_window))

        main_frame = ttk.Frame(data_window, padding="20 20 20 20", style='Transparent.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Gestión de Datos", font=('Arial', 18, 'bold'), foreground=TEXT_COLOR,
                  background=BACKGROUND_COLOR).pack(pady=(0, 20))

        top_frame = ttk.Frame(main_frame, style='Transparent.TFrame')
        top_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(top_frame, text="Seleccionar Tabla:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.table_combobox = ttk.Combobox(top_frame, values=["usuarios", "manuales", "registros"], state="readonly",
                                           width=30)
        self.table_combobox.pack(side=tk.LEFT)
        self.table_combobox.bind("<<ComboboxSelected>>", self.load_data)

        self.form_frame = ttk.LabelFrame(main_frame, text="Formulario", padding="10 10 10 10",
                                         style='Transparent.TLabelframe')
        self.form_frame.pack(fill=tk.X, pady=(0, 20))

        self.fields_frame = ttk.Frame(self.form_frame, style='Transparent.TFrame')
        self.fields_frame.pack(fill=tk.X, expand=True)

        button_frame = ttk.Frame(main_frame, style='Transparent.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 20))

        crud_buttons = [
            ("Crear", self.handle_create),
            ("Buscar", self.handle_read),
            ("Actualizar", self.handle_update),
            ("Eliminar", self.handle_delete),
            ("Limpiar", self.handle_clear)
        ]

        for text, command in crud_buttons:
            ttk.Button(button_frame, text=text, command=command, style='TButton').pack(side=tk.LEFT, padx=(0, 10))

        self.data_display_frame = ttk.Frame(main_frame, style='Transparent.TFrame')
        self.data_display_frame.pack(fill=tk.BOTH, expand=True)

        self.data_tree = create_data_tree(self.data_display_frame)
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        self.data_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tree_scroll = ttk.Scrollbar(self.data_display_frame, orient="vertical", command=self.data_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=tree_scroll.set)

        self.fields = {}
        self.create_form("usuarios")
        self.load_data()

    def create_menu(self):
        menubar = tk.Menu(self, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        menubar.add_cascade(label="Archivo", menu=file_menu, font=('Arial', 12))
        file_menu.add_command(label="Cerrar sesión", command=self.logout, font=('Arial', 12))
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing, font=('Arial', 12))

        view_menu = tk.Menu(menubar, tearoff=0, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        menubar.add_cascade(label="Ver", menu=view_menu, font=('Arial', 12))
        view_menu.add_command(label="Manuales de Mantenimiento", command=lambda: self.notebook.select(0),
                              font=('Arial', 12))
        view_menu.add_command(label="Gestión de Datos", command=lambda: self.notebook.select(1), font=('Arial', 12))

    def logout(self):
        self.auth_manager.logout()
        self.withdraw()
        self.show_login_window()

    def on_closing(self):
        logging.debug("Cerrando la aplicación")
        self.db_connector.disconnect()
        self.parent.destroy()

    def create_form(self, table):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.fields = create_form(self.fields_frame, table)

        for widget in self.fields_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.configure(style='TEntry')
            elif isinstance(widget, ttk.Label):
                widget.configure(style='TLabel', background=BACKGROUND_COLOR)
            elif isinstance(widget, ttk.Combobox):
                widget.configure(style='TCombobox')
    def load_data(self, event=None):
        selected_table = self.table_combobox.get()
        if not selected_table:
            return

        self.create_form(selected_table)

        query = f"SELECT * FROM {selected_table}"
        rows = self.db_connector.execute_query(query)
        if rows:
            columns = list(rows[0].keys())
            if 'contrasena' in columns:
                for row in rows:
                    row['contrasena'] = '*****'
            update_data_tree(self.data_tree, rows, columns)

    def create_crud_buttons(self, parent):
        crud_button_frame = ttk.Frame(parent, padding=10)
        crud_button_frame.pack(pady=10, fill=tk.X)

        buttons = [
            ("Crear", self.handle_create),
            ("Buscar", self.handle_read),
            ("Actualizar", self.handle_update),
            ("Eliminar", self.handle_delete),
            ("Limpiar", self.handle_clear)
        ]

        for text, command in buttons:
            ttk.Button(crud_button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5, pady=5)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def load_manuals_list(self):
        query = "SELECT id_manual, titulo, ruta_preview FROM manuales"
        result = self.db_connector.execute_query(query)
        self.manuals_listbox.delete(0, tk.END)
        self.manual_previews = {}
        for manual in result:
            self.manuals_listbox.insert(tk.END, manual['titulo'])
            self.manual_previews[manual['titulo']] = manual['ruta_preview']

    def on_manual_select(self, event):
        selection = self.manuals_listbox.curselection()
        if selection:
            title = self.manuals_listbox.get(selection[0])
            query = "SELECT descripcion, ruta_archivo FROM manuales WHERE titulo = %s"
            result = self.db_connector.execute_query(query, (title,))
            if result:
                self.description_text.config(state='normal')
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert(tk.END, result[0]['descripcion'])
                self.description_text.config(state='disabled')

                # Actualizar la vista previa
                ruta_archivo = result[0]['ruta_archivo']
                if ruta_archivo and os.path.exists(ruta_archivo):
                    img = self.generate_preview(ruta_archivo)
                    if img:
                        photo = ImageTk.PhotoImage(img)
                        self.preview_label.config(image=photo)
                        self.preview_label.image = photo  # Mantener una referencia
                    else:
                        self.preview_label.config(image='')
                else:
                    self.preview_label.config(image='')


    def view_manual(self):
        selection = self.manuals_listbox.curselection()
        if selection:
            title = self.manuals_listbox.get(selection[0])
            query = "SELECT ruta_archivo FROM manuales WHERE titulo = %s"
            result = self.db_connector.execute_query(query, (title,))
            if result and result[0]['ruta_archivo']:
                os.startfile(result[0]['ruta_archivo'])
            else:
                messagebox.showerror("Error", "No se pudo abrir el archivo del manual.")

    def upload_manual(self):
        if not self.auth_manager.check_permission('dueños'):
            messagebox.showerror("Error", "No tienes permiso para subir manuales.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        try:
            logging.debug(f"Archivo seleccionado: {file_path}")

            # Extraer título y generar vista previa
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                title = self.extract_pdf_title(pdf_reader, file_path)
                logging.debug(f"Título extraído: {title}")

            preview_image = self.generate_preview(file_path)
            if preview_image is None:
                raise Exception("No se pudo generar la vista previa del PDF")
            logging.debug("Vista previa generada")

            # Guardar el archivo
            save_dir = config.MANUAL_UPLOAD_FOLDER
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            logging.debug(f"Directorio de guardado: {save_dir}")

            filename = os.path.basename(file_path)
            save_path = os.path.join(save_dir, filename)
            shutil.copy2(file_path, save_path)
            logging.debug(f"Archivo guardado en: {save_path}")

            # Guardar la vista previa
            preview_filename = f"preview_{os.path.splitext(filename)[0]}.png"
            preview_path = os.path.join(save_dir, preview_filename)
            preview_image.save(preview_path)
            logging.debug(f"Vista previa guardada en: {preview_path}")

            # Insertar en la base de datos
            query = "INSERT INTO manuales (titulo, descripcion, ruta_archivo, ruta_preview) VALUES (%s, %s, %s, %s)"
            params = (title, "", save_path, preview_path)
            logging.debug(f"Ejecutando query: {query}")
            logging.debug(f"Parámetros: {params}")
            result = self.db_connector.execute_query(query, params)
            logging.debug(f"Resultado de la inserción: {result}")

            if result is None or result == 0:
                raise Exception("No se pudo insertar el registro en la base de datos.")

            messagebox.showinfo("Éxito", f"Manual '{title}' subido correctamente.")
            self.load_manuals_list()
        except Exception as e:
            logging.error(f"Error al subir el manual: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar el manual en la base de datos: {str(e)}")
            if 'save_path' in locals() and os.path.exists(save_path):
                os.remove(save_path)
            if 'preview_path' in locals() and os.path.exists(preview_path):
                os.remove(preview_path)


    def extract_pdf_title(self, pdf_reader, file_path):
        if pdf_reader.metadata and '/Title' in pdf_reader.metadata:
            return pdf_reader.metadata['/Title']
        return os.path.splitext(os.path.basename(file_path))[0]

    def generate_preview(self, file_path):
        try:
            doc = fitz.open(file_path)
            first_page = doc.load_page(0)
            pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Aumenta el factor de escala
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            img.thumbnail((1200, 950))  # Aumenta el tamaño máximo de la miniatura
            return img
        except Exception as e:
            logging.error(f"Error al generar la vista previa: {str(e)}")
            return None

    def delete_manual(self):
        if not self.auth_manager.check_permission('dueños'):
            messagebox.showerror("Error", "No tienes permiso para eliminar manuales.")
            return

        selection = self.manuals_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un manual para eliminar.")
            return

        title = self.manuals_listbox.get(selection[0])
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar el manual '{title}'?"):
            try:
                query = "SELECT ruta_archivo, ruta_preview FROM manuales WHERE titulo = %s"
                result = self.db_connector.execute_query(query, (title,))
                if result:
                    file_path = result[0]['ruta_archivo']
                    preview_path = result[0]['ruta_preview']

                    # Eliminar el registro de la base de datos
                    delete_query = "DELETE FROM manuales WHERE titulo = %s"
                    delete_result = self.db_connector.execute_query(delete_query, (title,))

                    if delete_result is None or delete_result == 0:
                        raise Exception("No se pudo eliminar el manual de la base de datos.")

                    # Eliminar los archivos físicos
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(preview_path):
                        os.remove(preview_path)

                    messagebox.showinfo("Éxito", f"Manual '{title}' eliminado correctamente.")
                    self.load_manuals_list()
                    self.description_text.delete('1.0', tk.END)
                    self.description_text.config(state='disabled')
                    self.preview_label.config(image='')
                else:
                    raise Exception("No se encontró el manual en la base de datos.")
            except Exception as e:
                logging.error(f"Error al eliminar el manual: {str(e)}")
                messagebox.showerror("Error", f"No se pudo eliminar el manual: {str(e)}")

    def toggle_edit_description(self):
        if not self.auth_manager.check_permission('dueños'):
            messagebox.showerror("Error", "No tienes permiso para editar la descripción.")
            return

        if self.description_text.cget('state') == 'normal':
            self.description_text.config(state='disabled')
            self.edit_button.config(text="Editar Descripción")
            self.save_button.config(state='disabled')
        else:
            self.description_text.config(state='normal')
            self.edit_button.config(text="Cancelar Edición")
            self.save_button.config(state='normal')

    def save_description(self):
        if not self.auth_manager.check_permission('dueños'):
            messagebox.showerror("Error", "No tienes permiso para guardar la descripción.")
            return

        selection = self.manuals_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un manual para guardar la descripción.")
            return

        title = self.manuals_listbox.get(selection[0])
        new_description = self.description_text.get('1.0', tk.END).strip()

        try:
            query = "UPDATE manuales SET descripcion = %s WHERE titulo = %s"
            result = self.db_connector.execute_query(query, (new_description, title))
            if result is None or result == 0:
                raise Exception("No se pudo actualizar la descripción en la base de datos.")

            messagebox.showinfo("Éxito", "Descripción actualizada correctamente.")
            self.description_text.config(state='disabled')
            self.edit_button.config(text="Editar Descripción")
            self.save_button.config(state='disabled')
        except Exception as e:
            logging.error(f"Error al guardar la descripción: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar la descripción: {str(e)}")

    def handle_create(self):
        if not self.auth_manager.check_permission('docentes'):
            messagebox.showerror("Error", "No tienes permisos para realizar esta acción")
            return

        selected_table = self.table_combobox.get()
        values = [field.get() for label, field in self.fields.items()
                  if isinstance(field, (tk.Entry, ttk.Combobox)) and label != "ID Usuario"]

        if selected_table == "usuarios":
            proc_name = "InsertarUsuarios"
        elif selected_table == "manuales":
            proc_name = "InsertarManuales"
        elif selected_table == "registros":
            proc_name = "InsertarRegistros"
        else:
            messagebox.showerror("Error", "Tabla no válida")
            return

        result = self.db_connector.call_procedure(proc_name, values)
        if result is not None:
            messagebox.showinfo("Éxito", "Registro creado correctamente")
            self.load_data()
        else:
            messagebox.showerror("Error", "No se pudo crear el registro")

    def handle_read(self):
        selected_table = self.table_combobox.get()
        id_value = self.fields[list(self.fields.keys())[0]].get()

        if selected_table == "usuarios":
            proc_name = "BuscarUsuarios"
            params = (id_value,)
        elif selected_table == "manuales":
            proc_name = "BuscarManuales"
            params = (id_value,)
        elif selected_table == "registros":
            id_manual = self.fields["ID Manual"].get()
            id_usuario = self.fields["ID Usuario"].get()
            proc_name = "BuscarRegistros"
            params = (id_manual, id_usuario)
        else:
            messagebox.showerror("Error", "Tabla no válida")
            return

        result = self.db_connector.call_procedure(proc_name, params)
        if result:
            self.populate_fields(result[0], list(self.fields.keys())[1:])
            messagebox.showinfo("Éxito", "Registro encontrado")
        else:
            messagebox.showinfo("Información", "No se encontró el registro")

    def handle_update(self):
        if not self.auth_manager.check_permission('docentes'):
            messagebox.showerror("Error", "No tienes permisos para realizar esta acción")
            return

        selected_table = self.table_combobox.get()
        values = [field.get() for field in self.fields.values()]

        if selected_table == "usuarios":
            proc_name = "ActualizarUsuarios"
        elif selected_table == "manuales":
            proc_name = "ActualizarManuales"
        elif selected_table == "registros":
            proc_name = "ActualizarRegistros"
        else:
            messagebox.showerror("Error", "Tabla no válida")
            return

        result = self.db_connector.call_procedure(proc_name, values)
        if result is not None:
            messagebox.showinfo("Éxito", "Registro actualizado correctamente")
            self.load_data()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro")

    def handle_delete(self):
        if not self.auth_manager.check_permission('directivos'):
            messagebox.showerror("Error", "No tienes permisos para realizar esta acción")
            return

        selected_table = self.table_combobox.get()
        id_value = self.fields[list(self.fields.keys())[0]].get()

        if selected_table == "usuarios":
            proc_name = "BorrarUsuarios"
            params = (id_value,)
        elif selected_table == "manuales":
            proc_name = "BorrarManuales"
            params = (id_value,)
        elif selected_table == "registros":
            id_manual = self.fields["ID Manual"].get()
            id_usuario = self.fields["ID Usuario"].get()
            proc_name = "BorrarRegistros"
            params = (id_manual, id_usuario)
        else:
            messagebox.showerror("Error", "Tabla no válida")
            return

        result = self.db_connector.call_procedure(proc_name, params)
        if result is not None:
            messagebox.showinfo("Éxito", "Registro eliminado correctamente")
            self.load_data()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el registro")

    def handle_clear(self):
        for field in self.fields.values():
            field.delete(0, tk.END)

    def on_tree_select(self, event):
        selected_item = self.data_tree.selection()[0]
        values = self.data_tree.item(selected_item)['values']
        self.populate_fields(values, list(self.fields.keys()))

    def populate_fields(self, values, fields):
        for value, field in zip(values, fields):
            self.fields[field].delete(0, tk.END)
            self.fields[field].insert(0, str(value))

    def close_data_management(self, window):
        window.destroy()