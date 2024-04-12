import os
from fastapi import FastAPI
from gridfs import GridFS
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pymongo import MongoClient

app = FastAPI()
# Cargar variables de entorno desde el archivo .env
load_dotenv()
config = {'NEO4J_URI': os.getenv('NEO4J_URI'), 'NEO4J_USER': os.getenv('NEO4J_USERNAME'),
          'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'), 'MONGO_URI': os.getenv('MONGO_URI')}

neo4j_driver = GraphDatabase.driver(config['NEO4J_URI'],
                                    auth=(config['NEO4J_USER'], config['NEO4J_PASSWORD']))
mongo_client = MongoClient(config['MONGO_URI'])
db = mongo_client['social_network']
grid_fs = GridFS(db)
