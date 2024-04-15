from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class updateUser(BaseModel):
    properties: Dict[str, Any] = Field(..., example={"name": "Alice", "age": 33})
    labels: Optional[List[str]] = Field(..., example=["Person"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "properties": {
                        "name": "Alice",
                        "age": 33,
                    },
                    "labels": ["Person"]
                }
            ]
        }
    }


class updateRelations(BaseModel):
    username: str = Field(..., example="Alice")
    role: Optional[str] = Field('', example="admin")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "properties": {
                        "name": "Alice",
                        "age": 33,
                    },
                    "labels": ["Person"]
                }
            ]
        }
    }