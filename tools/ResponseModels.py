from pydantic import BaseModel
from typing import List, Dict, Any


class basicResponse(BaseModel):
    status: str
    operation: str = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success to `operation` node",
                }
            ]
        }
    }


class searchNodesModel(BaseModel):
    status: str
    nodes: List[Dict[str, Any]]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "nodes": [
                        {
                            "labels": ["Person"],
                            "properties": {
                                "name": "Alice",
                                "age": 33,
                            },
                        },
                        {
                            "labels": ["Person"],
                            "properties": {
                                "name": "Bob",
                                "age": 44,
                            },
                        }
                    ]
                }
            ]
        }
    }


# Modelo para la respuesta de éxito al subir archivo
class UploadResponse(BaseModel):
    status: str
    file_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "file_id": "66160600feefbe5bdc608623"
                }
            ]
        }
    }


class getIdGrid(BaseModel):
    filename: str
    file_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filename": "grid.png",
                    "file_id": "66160600feefbe5bdc608623"
                }
            ]
        }
    }
