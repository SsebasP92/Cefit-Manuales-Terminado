from PIL import Image, ImageTk
import os


def get_project_root():
    # Ajusta esto según la estructura de tu proyecto
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_and_resize_image(image_name, size):
    root_dir = get_project_root()
    image_path = os.path.join(root_dir, 'images', image_name)

    try:
        image = Image.open(image_path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except IOError:
        print(f"No se pudo cargar la imagen: {image_path}")
        return None


def get_login_background(size=(1200, 700)):
    return load_and_resize_image('cefit308.jpeg', size)


def get_icon():
    root_dir = get_project_root()
    return os.path.join(root_dir, 'images', 'iconoproyecto.ico')
