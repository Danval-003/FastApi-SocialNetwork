import re
import warnings

from bson import ObjectId
from fastapi import APIRouter, HTTPException, UploadFile
from starlette.responses import StreamingResponse
from tools import UploadResponse, basicResponse, getIdGrid
from basics import grid_fs
from werkzeug.utils import secure_filename

gridR = APIRouter()


@gridR.post("/upload/", response_model=UploadResponse, response_model_exclude_unset=True)
async def upload_file(file: UploadFile = None):
    try:
        filename = secure_filename(file.filename)  # Nombre de archivo seguro (podrías obtenerlo desde la solicitud)
        content_type = file.content_type  # Tipo de contenido por defecto para el archivo

        # Guardar el archivo en GridFS
        file_id = grid_fs.put(file, filename=filename, content_type=content_type)

        return UploadResponse(file_id=str(file_id), status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@gridR.get("/download/{file_id}/", response_class=StreamingResponse,  responses={
    200: {
        "content": {
            "application/octet-stream": {
                "example": b"Archivo binario aqui...",
            }
        },
        "description": "Archivo descargado correctamente."
    }
})
async def download_file(file_id: str):
    id_file = ObjectId(file_id)
    warnings.warn(str(id_file))
    warnings.warn(file_id)
    try:
        # Buscar el archivo en GridFS por su ID
        file_data = grid_fs.get(id_file)
        if file_data is None:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Preparar el contenido del archivo como una respuesta de transmisión
        return StreamingResponse(
            grid_fs.get(id_file),
            media_type=file_data.content_type,
            headers={"Content-Disposition": f"attachment; filename={file_data.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@gridR.delete("/delete/{file_id}/", response_model=basicResponse, response_model_exclude_unset=True)
async def delete_file(file_id: str, ):
    id_file = ObjectId(file_id)
    try:
        # Eliminar el archivo de GridFS
        grid_fs.delete(id_file)
        return basicResponse(status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@gridR.get("/get_id_by_filename/{filename}", response_model=getIdGrid, response_model_exclude_unset=True)
async def get_id_by_filename(filename: str):
    try:
        # Buscar el archivo en GridFS por su nombre de archivo
        file_data = grid_fs.find_one({"filename": filename})
        if file_data is None:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Obtener el ID del archivo
        file_id = str(file_data._id)
        return getIdGrid(file_id=file_id, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Función para generar los fragmentos del archivo
async def generate_file_content(file_id: ObjectId, start: int = 0, end: int = None):
    try:
        # Buscar el archivo en GridFS por su ID
        file_data = grid_fs.get(file_id)
        if file_data is None:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Obtener el tamaño total del archivo
        total_size = file_data.length

        # Calcular el rango de bytes a leer
        if end is None or end >= total_size:
            end = total_size - 1

        # Asegurarse de que los valores de inicio y fin estén dentro de los límites
        start_range, end_range = parse_range_header(None, total_size)

        if start_range is None:
            start_range = 0
        if end_range is None or end_range >= total_size:
            end_range = total_size - 1
        length = end_range - start_range + 1

        # Calcular la longitud del contenido
        content_length = end_range - start_range + 1

        # Configurar encabezados de respuesta
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Type': file_data.content_type,
            'Content-Length': str(content_length),
            'Content-Range': f'bytes {start}-{end}/{total_size}'
        }

        # Función de generador para transmitir los datos en fragmentos
        async def stream_file_():
            chunk_size = 8192  # Tamaño del bloque de lectura (bytes)
            bytes_sent = 0
            file_data.seek(start)  # Mover el cursor al inicio del rango solicitado

            while bytes_sent < content_length:
                # Leer un bloque del archivo
                remaining_bytes = content_length - bytes_sent
                current_chunk_size = min(chunk_size, remaining_bytes)
                chunk = file_data.read(current_chunk_size)

                if not chunk:
                    break  # Si no hay más datos para leer, salir del bucle

                bytes_sent += len(chunk)
                yield chunk

        # Devolver una respuesta de transmisión con los datos del archivo
        return StreamingResponse(stream_file_(), headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_range_header(range_header, file_size):
    if not range_header:
        return None, None

    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if range_match:
        start_range = int(range_match.group(1))
        end_range = int(range_match.group(2)) if range_match.group(2) else None
        if end_range and end_range >= file_size:
            end_range = file_size - 1
        return start_range, end_range

    return None, None


@gridR.get("/stream/{file_id}/", response_class=StreamingResponse,  responses={
    200: {
        "content": {
            "application/octet-stream": {
                "example": b"Archivo binario aqui...",
            }
        },
        "description": "Visualization of content."
    }
})
async def stream_file(file_id: str):
    id_file = ObjectId(file_id)
    try:
        return await generate_file_content(id_file)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
