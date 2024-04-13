from typing import List

from starlette.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from basics import app
from routes import create, delete, read, update
from gridfs_routes import gridR
from tools import makeQuery, node
from

app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")
app.include_router(create, prefix="/create", tags=["create"])
app.include_router(delete, prefix="/delete", tags=["delete"])
app.include_router(read, prefix="/search", tags=["search"])
app.include_router(update, prefix="/update", tags=["update"])
app.include_router(gridR, prefix="/multimedia", tags=["multimedia"])


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
