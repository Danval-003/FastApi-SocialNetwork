import json
import uuid
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, File, UploadFile, Body, Form, Depends
from tools import node, basicResponse, createRelationship, NodeD, relationship, makeQuery
from werkzeug.utils import secure_filename

from tools import createNode, user_person, format_properties
from basics import grid_fs, origin
create = APIRouter()


@create.post('/node', response_model=basicResponse)
async def create_node(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels
        merge: bool = N.merge

        createNode(labels, properties, merge)
        response_data = {'status': 'success to create node'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/nodes', response_model=basicResponse, response_model_exclude_unset=True)
async def create_nodes(Ns: List[node]):
    try:
        for N in Ns:
            properties: Dict[str, Any] = N.properties
            labels: List[str] = N.labels
            merge: bool = N.merge

            createNode(labels, properties, merge)
        response_data = {'status': f'success to create {len(Ns)} nodes'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/relationship', response_model=basicResponse, response_model_exclude_unset=True)
async def create_relationship(R: relationship):
    try:
        properties: Dict[str, Any] = R.properties
        type_r: str = R.type
        node1: node = R.node1
        node2: node = R.node2

        createRelationship(typeR=type_r, properties=properties, node1=NodeD(node1.labels, node1.properties), node2=NodeD(node2.labels, node2.properties))
        response_data = {'status': 'success to create relationship'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/user/person', response_model=basicResponse, response_model_exclude_unset=True)
async def create_user_person(U: user_person = Depends(), profile_image: UploadFile = None):
    try:
        properties: Dict[str, Any] = U.dict()
        labels: List[str] = ['User', 'Person']
        properties['profile_image'] = origin+"/multimedia/stream/661995a854e08ee44bee3bda/"
        properties['userId'] = str(uuid.uuid4())

        if profile_image:
            file_data = await profile_image.read()
            filename = secure_filename(profile_image.filename)
            content_type = profile_image.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['profile_image'] = origin+"multimedia/stream/"+str(file_id)+"/"


        createNode(labels, properties, merge=True)
        response_data = {'status': f'success to create user person with id {properties['userId']}'}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))



