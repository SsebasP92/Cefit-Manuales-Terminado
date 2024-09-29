import logging
import tkinter as tk
import config
from database.connector import DatabaseConnector
from gui.main_window import MainWindow
from gui.utils import set_icon
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Desactiva el límite

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def main():
    root = tk.Tk()
    root.withdraw()
    root.geometry("1600x900")
    set_icon(root)
    db_connector = None
    try:
        logging.debug("Iniciando la aplicación")
        db_connector = DatabaseConnector(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        db_connector.connect()
        logging.debug("Conexión a la base de datos establecida")
        app = MainWindow(root, db_connector)
        logging.debug("Ventana principal creada")

        root.mainloop()
        logging.debug("Mainloop finalizado")
    except Exception as e:
        logging.exception(f"Error al iniciar la aplicación: {e}")
    finally:
        if db_connector:
            db_connector.disconnect()
        logging.debug("Aplicación cerrada")
if __name__ == "__main__":
    main()