from typing import List

from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from basics import app
from routes import create, delete, read, update, loginUtilities
from gridfs_routes import gridR
from tools import makeQuery, node

app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")
app.include_router(create, prefix="/create", tags=["create"])
app.include_router(delete, prefix="/delete", tags=["delete"])
app.include_router(read, prefix="/search", tags=["search"])
app.include_router(update, prefix="/update", tags=["update"])
app.include_router(gridR, prefix="/multimedia", tags=["multimedia"])
app.include_router(loginUtilities, prefix="/login", tags=["login"])

# Configuración de CORS para permitir todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Received request: {request.method} {request.url}")

    # Obtener los datos del cuerpo de la solicitud (FormData)
    form_data = await request.form()
    print(f"FormData: {form_data}")

    # Recorrer y loguear cada campo y valor del FormData
    for field in form_data:
        value = form_data.get(field)
        print(f"FormData field: {field}, value: {value}")

    # Continuar con el procesamiento de la solicitud
    response = await call_next(request)

    # Loguear información sobre la respuesta enviada
    print(f"Sent response: {response.status_code}")

    return response




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# Ruta para servir el favicon.ico
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get('/api/nodos', response_model=List[node], response_model_exclude_unset=True)
def obtener_nodos():
    nodes = []
    for n in makeQuery():
        nodes.append(node(**n[0].to_json()))

    return nodes
