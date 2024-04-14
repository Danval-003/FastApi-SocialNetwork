from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from tools import node


class basicResponse(BaseModel):
    status: str
    operation: str = None
    id: Optional[str] = None
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
    nodes: List[node]
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


class relationShipModel(BaseModel):
    typeR: str
    nodeTo: node
    nodeFrom: node
    properties: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "typeR": "KNOWS",
                    "nodeTo": {
                        "labels": ["Person"],
                        "properties": {
                            "name": "Alice",
                            "age": 33,
                        },
                    },
                    "nodeFrom": {
                        "labels": ["Person"],
                        "properties": {
                            "name": "Bob",
                            "age": 44,
                        },
                    },
                    "properties": {
                        "since": "2020-01-01",
                    }
                }
            ]
        }
    }


class searchRelationshipsModel(BaseModel):
    status: str
    relationships: List[relationShipModel]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "relationships": [
                        {
                            "typeR": "KNOWS",
                            "nodeTo": {
                                "labels": ["Person"],
                                "properties": {
                                    "name": "Alice",
                                    "age": 33,
                                },
                            },
                            "nodeFrom": {
                                "labels": ["Person"],
                                "properties": {
                                    "name": "Bob",
                                    "age": 44,
                                },
                            },
                            "properties": {
                                "since": "2020-01-01",
                            }
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
