import datetime

from fastapi import UploadFile
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class node(BaseModel):
    labels: List[str] = []
    properties: Dict[str, Any] = {}
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
    language: str = Field(..., example="es", description="Language of the user")
    isVerified: bool = Field(..., example=False, description="Is the user verified?")
    password: str = Field(..., example="123456", description="Password of the user")
    username: str = Field(..., example="dinamo", description="Username of the user")
    name: str = Field(..., example="Dinamo", description="Full name of the user")
    age: int = Field(..., example=33, description="Age of the user")
    occupation: str = Field(..., example="Developer", description="Job of the user")
    location: str = Field(..., example="Madrid", description="Location of the user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "language": "es",
                    "isVerified": False,
                    "password": "123456+",
                    "username": "dinamo",
                    "name": "Dinamo",
                    "age": 33,
                    "occupation": "Developer",
                    "location": "Madrid"
                },
                {
                    "language": "es",
                    "isVerified": False,
                    "password": "123456+",
                    "username": "dinamo",
                    "name": "Dinamo",
                    "age": 33,
                    "occupation": "Developer",
                    "location": "Madrid"
                }
            ]
        }
    }


class user_organization(BaseModel):
    language: str = Field(..., example="es", description="Language of the user")
    isVerified: bool = Field(..., example=False, description="Is the user verified?")
    password: str = Field(..., example="123456", description="Password of the user")
    name: str = Field(..., example="Dinamo", description="Name of the organization")
    username: str = Field(..., example="Dinamo", description="Name of the organization")
    website: str = Field(..., example="https://dinamo.com", description="URL of the website")
    contact: str = Field(..., example="Contact info", description="Contact info of the organization")
    orgType: str = Field(..., example="IT", description="Type of the user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "dimo@gmail.com",
                    "language": "es",
                    "isVerified": False,
                    "password": "123456+",
                    "name": "Dinamo",
                    "username": "Dinamo",
                    "website": "https://dinamo.com",
                    "contact": "Contact info",
                    "orgType": "IT"
                }
            ]
        }
    }


class postNode(BaseModel):
    textContent: str = Field(..., example="Hello", description="Content of the post")
    isPrivate: bool = Field(..., example=False, description="Is the post private?")
    hashtags: str = Field(..., example="", description="List of hashtags split with #")


class loginModel(BaseModel):
    username: str = Field(..., example="dinamo", description="Email of the user")
    password: str = Field(..., example="123", description="Password of the user")


class affiliate(BaseModel):
    role: Optional[str] = Field(..., example="admin", description="Role of the affiliate")
    name: str = Field(..., example="123", description="ID of the organization")


class follow(BaseModel):
    username: str = Field(..., example="dinamo", description="Username of the user")


class like(BaseModel):
    idPost: str = Field(..., example="123", description="ID of the post")
    positive: Optional[bool] = Field(..., example=True, description="Positive or negative like")


class onlyIdPost(BaseModel):
    idPost: str = Field(..., example="123", description="ID of the post")

class relationPost(BaseModel):
    idPost: str = Field(..., example="123", description="ID of the post")
    relationType : str = Field(..., example="KNOWS", description="Type of the relation")

class relationSearch(BaseModel):
    relationType : str = Field(..., example="KNOWS", description="Type of the relation")
    labels: List[str] = Field([], example=["Person"], description="Labels of the node")

class searchLIMIT(BaseModel):
    search: Optional[str] = Field('', example="Dinamo", description="Search query")
    skip: Optional[int] = Field(0, example=0, description="Skip the first n results")
    limit: Optional[int] = Field(10, example=10, description="Limit the results to n")


class commentNode(BaseModel):
    textContent: str = Field(..., example="Hello", description="Content of the post")
    isPrivate: bool = Field(..., example=False, description="Is the post private?")
    language: str = Field(..., example="es", description="Language of the user")
    idDepend: str = Field(..., example="123", description="ID of the post")


class updateStatus(BaseModel):
    status: Optional[str] = Field('', example="Hello", description="Content of the post")
