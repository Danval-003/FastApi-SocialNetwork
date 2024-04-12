import os
import uuid
from basics import grid_fs


def upload_file(file):
    filename = file.filename
    file_ext = os.path.splitext(filename)[1]  # Obtener la extensión del archivo
    unique_filename = str(uuid.uuid4()) + file_ext  # Generar un nombre único
    grid_fs.put(file, filename=unique_filename, content_type=file.content_type)
    return unique_filename
