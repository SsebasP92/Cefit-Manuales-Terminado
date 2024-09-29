from tkinter import ttk
import logging
def create_data_tree(parent):
    data_tree = ttk.Treeview(parent, columns=[], show="headings")
    data_tree.pack(fill="both", expand=True)
    logging.debug("Treeview creado")
    return data_tree
def update_data_tree(data_tree, data, columns):
    logging.debug(f"Actualizando Treeview con {len(data)} filas y columnas: {columns}")
    data_tree["columns"] = columns
    for col in columns:
        data_tree.heading(col, text=col)
    for item in data_tree.get_children():
        data_tree.delete(item)
    for row in data:
        data_tree.insert("", "end", values=[row[col] for col in columns])
    logging.debug("Treeview actualizado")