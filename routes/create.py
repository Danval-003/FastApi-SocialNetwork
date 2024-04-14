import uuid
from datetime import datetime
from typing import List, Dict, Any

import bcrypt
from fastapi import APIRouter, HTTPException, UploadFile, Depends
from langdetect import detect
from starlette.requests import Request
from werkzeug.utils import secure_filename

from basics import grid_fs, origin
from loginUtilities import BearerAuthMiddleware
from tools import createNode, user_organization, user_person, postNode, affiliate
from tools import node, basicResponse, createRelationship, NodeD, relationship, makeQuery, format_properties

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

        createRelationship(typeR=type_r, properties=properties, node1=NodeD(node1.labels, node1.properties),
                           node2=NodeD(node2.labels, node2.properties))
        response_data = {'status': 'success to create relationship'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/user/person', response_model=basicResponse, response_model_exclude_unset=True)
async def create_user_person(U: user_person = Depends(), profile_image: UploadFile = None):
    print("ASDASDAD")
    try:
        query = f"MATCH (u:User:Person {format_properties({"username": U.username})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="User with this username already exists")

        query = f"MATCH (u:User:Person {format_properties({"email": U.email})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        properties: Dict[str, Any] = U.dict()
        labels: List[str] = ['User', 'Person']
        properties['profile_image'] = origin + "multimedia/stream/661995a854e08ee44bee3bda/"
        properties['userId'] = str(uuid.uuid4())
        properties['password'] = hash_password(properties['password'])
        properties['resgisterDate'] = str(datetime.date(datetime.now()))
        properties['mutualCount'] = 0
        properties['followCount'] = 0
        properties['followerCount'] = 0

        if profile_image:
            file_data = await profile_image.read()
            filename = secure_filename(profile_image.filename)
            content_type = profile_image.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['profile_image'] = origin + "multimedia/stream/" + str(file_id) + "/"

        createNode(labels, properties, merge=True)
        response_data = {'status': f'success to create user person with id {properties['userId']}'}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/user/organization', response_model=basicResponse, response_model_exclude_unset=True)
async def create_user_organization(U: user_organization = Depends(), profile_image: UploadFile = None):
    try:
        query = f"MATCH (u:User:Organization {format_properties({'name': U.name})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="Organization with this name already exists")

        query = f"MATCH (u:User:Organization {format_properties({'email': U.email})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="Organization with this email already exists")

        properties: Dict[str, Any] = U.dict()
        labels: List[str] = ['User', 'Organization']
        properties['logo_image'] = origin + "multimedia/stream/661995a854e08ee44bee3bda/"
        properties['userId'] = str(uuid.uuid4())
        properties['password'] = hash_password(properties['password'])
        properties['resgisterDate'] = str(datetime.date(datetime.now()))
        properties['followCount'] = 0
        properties['followerCount'] = 0

        if profile_image:
            file_data = await profile_image.read()
            filename = secure_filename(profile_image.filename)
            content_type = profile_image.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['logo_image'] = origin + "multimedia/stream/" + str(file_id) + "/"

        createNode(labels, properties, merge=True)
        response_data = {'status': f'success to create user Organization with id {properties['userId']}'}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/post/', dependencies=[Depends(BearerAuthMiddleware())])
async def makePost(request: Request, P: postNode = Depends(), multimedia: List[UploadFile] = None):
    try:
        userID = request.state.user.properties['userId']
        properties: Dict[str, Any] = P.dict()
        labels: List[str] = ['Post']
        properties['postId'] = str(uuid.uuid4())
        properties['multimedia'] = []
        properties['language'] = detect(properties['textContent'])
        properties['likes'] = 0
        properties['views'] = 0

        if multimedia is None:
            multimedia = []

        for media in multimedia:
            file_data = await media.read()
            filename = secure_filename(media.filename)
            content_type = media.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['multimedia'].append(origin + "multimedia/stream/" + str(file_id) + "/")

        createNode(labels, properties, merge=True)
        createRelationship(typeR='POSTED', properties={}, node1=NodeD(['User'], {'userId': userID}),
                           node2=NodeD(['Post'], {'postId': properties['postId']}))
        response_data = {'status': f'success to create post with id {properties["postId"]}'}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/affiliate', dependencies=[Depends(BearerAuthMiddleware())])
async def create_affiliate(request: Request, af: affiliate):
    try:
        properties: Dict[str, Any] = af.dict()
        properties['affiliatedDate'] = datetime.date(datetime.now())
        typeR = 'AFFILIATE'
        userId = request.state.user.properties['userId']
        organizationName = properties['name']

        createRelationship(typeR=typeR, properties=properties, node1=NodeD(['User'], {'userId': userId}),
                           node2=NodeD(['User'], {'name': organizationName}))

        response_data = {'status': f'success to create affiliate with id {properties["idOrganization"]}'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


# Función para hashear una contraseña y generar una sal
def hash_password(password):
    # Generar una sal aleatoria
    salt = bcrypt.gensalt()
    # Hashear la contraseña con la sal
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password_str = hashed_password.hex()
    return hashed_password_str  # Devuelve el hash como una cadena hexadecimal
