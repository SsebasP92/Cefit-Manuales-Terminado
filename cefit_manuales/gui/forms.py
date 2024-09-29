import tkinter as tk
from tkinter import ttk
import logging
def create_form(parent, table):
    logging.debug(f"Creando formulario para la tabla: {table}")
    fields = {}
    if table == "usuarios":
        labels = ["ID Usuario", "Tipo Documento", "Número Documento", "Nombre", "Correo", "Contraseña", "Rol"]
        for idx, label in enumerate(labels):
            tk.Label(parent, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)
            if label == "Tipo Documento":
                entry = ttk.Combobox(parent, values=["CC", "TI", "CE", "PPT"])
            elif label == "Rol":
                entry = ttk.Combobox(parent, values=["dueños", "docentes", "directivos", "usuario"])
            elif label == "Contraseña":
                entry = tk.Entry(parent, show="*")
            else:
                entry = tk.Entry(parent)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=tk.EW)
            fields[label] = entry
    elif table == "manuales":
        labels = ["ID Manual", "Titulo", "Descripcion", "Ruta Archivo"]
        for idx, label in enumerate(labels):
            tk.Label(parent, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(parent)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=tk.EW)
            fields[label] = entry
    elif table == "registros":
        labels = ["ID Manual", "ID Usuario", "Fecha Acceso"]
        for idx, label in enumerate(labels):
            tk.Label(parent, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(parent)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=tk.EW)
            fields[label] = entry
    logging.debug(f"Formulario creado con campos: {list(fields.keys())}")
    return fields