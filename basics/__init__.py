import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gridfs import GridFS
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext
from starlette import status

app = FastAPI()
# Cargar variables de entorno desde el archivo .env
load_dotenv()
origin = os.getenv('ORIGIN_URL')
config = {'NEO4J_URI': os.getenv('NEO4J_URI'), 'NEO4J_USER': os.getenv('NEO4J_USERNAME'),
          'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'), 'MONGO_URI': os.getenv('MONGO_URI')}

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokenConfig = {'SECRET_KEY': SECRET_KEY, 'ALGORITHM': ALGORITHM,
               'ACCESS_TOKEN_EXPIRE_MINUTES': ACCESS_TOKEN_EXPIRE_MINUTES}


# Función para crear token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


"""neo4j_driver = GraphDatabase.driver(config['NEO4J_URI'],
                                    auth=(config['NEO4J_USER'], config['NEO4J_PASSWORD']))"""
mongo_client = MongoClient(config['MONGO_URI'])
db = mongo_client['social_network']
grid_fs = GridFS(db)
neo4j_driver = None

