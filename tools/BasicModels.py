import datetime

from pydantic import BaseModel
from typing import List, Dict, Any


class node(BaseModel):
    labels: List[str]
    properties: Dict[str, Any]
    merge: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "labels": ["Person"],
                    "properties": {
                        "name": "Alice",
                        "age": 33,
                    },
                    "merge": False
                }
            ]
        }
    }


class relationship(BaseModel):
    type: str
    properties: Dict[str, Any]
    node1: node
    node2: node

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "KNOWS",
                    "properties": {
                        "since": 2010,
                    },
                    "node1": {
                        "labels": ["Person"],
                        "properties": {
                            "name": "Alice",
                            "age": 33,
                        },
                        "merge": False
                    },
                    "node2": {
                        "labels": ["Person"],
                        "properties": {
                            "name": "Bob",
                            "age": 44,
                        },
                        "merge": False
                    }
                }
            ]
        }
    }


class user_person(BaseModel):
    email: str
    followerCount: int
    registerDate: datetime.date
    language: str
    isVerified: bool
    followCount: int
    password: str
    mutualCount: int
    username: str
    fullName: str
    age: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "diname@gmail.com",
                    "followerCount": 0,
                    "registerDate": "2021-06-16",
                    "language": "es",
                    "isVerified": False,
                    "followCount": 0,
                    "password": "123456",
                    "mutualCount": 0,
                    "username": "Diname",
                    "fullName": "Diname",
                    "age": 22
                }
            ]
        }
    }



