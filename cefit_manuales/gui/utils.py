import os
from PIL import Image, ImageTk
from PIL._tkinter_finder import tk
def set_icon(window):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, '..', 'images', 'iconoproyecto.ico')

        if os.path.exists(icon_path):
            window.iconbitmap(icon_path)
        else:
            raise FileNotFoundError(f"El archivo de icono no se encuentra en: {icon_path}")
    except tk.TclError:
        try:
            icon = ImageTk.PhotoImage(Image.open(icon_path))
            window.iconphoto(False, icon)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")