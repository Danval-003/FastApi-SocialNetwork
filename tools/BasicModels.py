import datetime

from pydantic import BaseModel, Field
from typing import List, Dict, Any


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
    email: str = Field(..., example="dinamo@gmail.com", description="Email of the user")
    language: str = Field(..., example="es", description="Language of the user")
    isVerified: bool = Field(..., example=False, description="Is the user verified?")
    password: str = Field(..., example="123456", description="Password of the user")
    username: str = Field(..., example="dinamo", description="Username of the user")
    fullName: str = Field(..., example="Dinamo", description="Full name of the user")
    age: int = Field(..., example=33, description="Age of the user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "figos@gmail.com",
                    "language": "es",
                    "isVerified": False,
                    "password": "123456",
                    "username": "figos",
                    "fullName": "Figo",
                    "age": 33
                }
            ]
        }
    }


class user_organization(BaseModel):
    email: str = Field(..., example="dinamo@gmail.com", description="Email of the user")
    language: str = Field(..., example="es", description="Language of the user")
    isVerified: bool = Field(..., example=False, description="Is the user verified?")
    password: str = Field(..., example="123456", description="Password of the user")
    name: str = Field(..., example="Dinamo", description="Name of the organization")
    websiteUrl: str = Field(..., example="https://dinamo.com", description="URL of the website")
    contactInfo: str = Field(..., example="Contact info", description="Contact info of the organization")
    typeOrg: str = Field(..., example="IT", description="Type of the user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "hello@hello.com",
                    "followerCount": 0,
                    "registerDate": "2021-06-15",
                    "language": "es",
                    "isVerified": False,
                    "followCount": 0,
                    "password": "123456",
                    "name": "Dinamo",
                    "websiteUrl": "https://dinamo.com",
                    "contactInfo": "Contact info",
                    "typeOrg": "IT"
                }
            ]
        }
    }


class postNode(BaseModel):
    textContent: str = Field(..., example="Hello", description="Content of the post")
    isPrivate: bool = Field(..., example=False, description="Is the post private?")


class hashtag(BaseModel):
    name: str = Field(..., example="hello", description="Name of the hashtag")
    postCount: int = Field(..., example=0, description="Number of posts")
    creationDate: str = Field(..., example=str(datetime.date.today()), description="Date of creation")
    country: str = Field(..., example="US", description="Country of the hashtag")
    engagementRate: float = Field(..., example=0.0, description="Engagement rate of the hashtag")


class loginModel(BaseModel):
    email: str = Field(..., example="figo@gmail.com", description="Email of the user")
    password: str = Field(..., example="123", description="Password of the user")



