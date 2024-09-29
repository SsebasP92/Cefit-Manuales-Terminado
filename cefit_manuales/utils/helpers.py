import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

def validate_input(data, table):
    logging.debug(f"Validando entrada para tabla {table}: {data}")
    if table == "usuarios":
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('correo', '')):
            raise ValueError("Formato de correo electrónico inválido")
        if len(data.get('contrasena', '')) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if data.get('rol') not in ['dueños', 'docentes', 'directivos', 'usuario']:
            raise ValueError("Rol no válido")
    elif table == "manuales":
        if not data.get('titulo', '').strip():
            raise ValueError("El título del manual no puede estar vacío")
        if not data.get('ruta_archivo', '').strip():
            raise ValueError("La ruta del archivo no puede estar vacía")
    elif table == "registros":
        try:
            datetime.strptime(data.get('fecha_acceso', ''), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS")
    logging.debug("Validación exitosa")
    return True

def format_data_for_display(data):
    logging.debug(f"Formateando datos para mostrar: {data}")
    formatted_data = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            formatted_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, str) and len(value) > 50:
            formatted_data[key] = value[:47] + "..."
        else:
            formatted_data[key] = value
    logging.debug(f"Datos formateados: {formatted_data}")
    return formatted_data

def sanitize_filename(filename):
    """
    Sanitiza el nombre del archivo eliminando caracteres no permitidos.
    """
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def is_valid_pdf(file_path):
    """
    Verifica si el archivo es un PDF válido.
    """
    try:
        with open(file_path, 'rb') as file:
            header = file.read(5)
            return header == b'%PDF-'
    except Exception as e:
        logging.error(f"Error al verificar el archivo PDF: {e}")
        return False