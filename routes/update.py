from fastapi import APIRouter, HTTPException, Depends, UploadFile
import bcrypt
from starlette.requests import Request
from werkzeug.utils import secure_filename

from tools import detachDeleteNode, node, basicResponse, UpdateModels, makeQuery, format_properties, updateStatus
from typing import Dict, Any, List
from loginUtilities import BearerAuthMiddleware
from basics import grid_fs, origin

update = APIRouter()


@update.post('/node', response_model=basicResponse, response_model_exclude_unset=True)
async def update_node(N: node):
    properties: Dict[str, Any] = N.properties
    labels: List[str] = N.labels
    detachDeleteNode(properties, labels)

    return basicResponse(status='success to update node')


@update.post('/user/', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def update_user(Up: UpdateModels.updateUser, request: Request):
    try:
        userId = request.state.user.properties['userId']
        propsLast = request.state.user.properties
        properties: Dict[str, Any] = {key: value for key, value in Up.properties.items() if value is not None and
                                      key in propsLast and key != 'userId' and key != 'profile_image'}

        def format(props):
            format_ = ''
            for key, value in props.items():
                if key == 'password':
                    value = hash_password(str(value))

                if type(value) == str:
                    format_ += f"n.{key} = '{value}', "
                elif type(value) == int:
                    format_ += f"n.{key} = {value}, "
                elif type(value) == bool:
                    format_ += f"n.{key} = {str(value).lower()}, "
                elif type(value) == float:
                    format_ += f"n.{key} = {value}, "

            if format_[-2:] == ', ':
                format_ = format_[:-2]
            return format_

        query = f"MATCH (n:User {format_properties({'userId': userId})}) SET {format(properties)} RETURN n"
        makeQuery(query, listOffIndexes=['n'])
        return basicResponse(status='success to update user')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@update.post('/user/profileImage', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def update_profile_image(newProfileImage: UploadFile, request: Request):
    try:
        userId = request.state.user.properties['userId']
        if newProfileImage is None:
            raise HTTPException(status_code=400, detail="No file provided")

        file_data = await newProfileImage.read()
        filename = secure_filename(newProfileImage.filename)
        content_type = newProfileImage.content_type

        with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
            grid_file.write(file_data)
            file_id = grid_file._id

        properties = {'profile_image': origin + "multimedia/stream/" + str(file_id) + "/"}

        query = f"MATCH (n:User {format_properties({'userId': userId})}) SET n.profile_image = '{properties['profile_image']}' RETURN n"
        makeQuery(query, listOffIndexes=['n'])
        return basicResponse(status='success to update profile image')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@update.post('/user/affiliate/', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def update_user(Up: UpdateModels.updateRelations, request: Request):
    try:
        userId = request.state.user.properties['userId']
        orgUsername = Up.username

        query = f"MATCH (n:User {format_properties({'userId': userId})}) - [r:AFFILIATE] -> (o:User:Organization {format_properties({'username': orgUsername})}) "

        if Up.role == '':
            query += "REMOVE r.role"
        else:
            query += f"SET r.role = '{Up.role}'"

        query += " RETURN n"
        makeQuery(query, listOffIndexes=['n'])
        return basicResponse(status='success to update user')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@update.post('/status/', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def update_status(Up: updateStatus, request:Request):
    try:
        userId = request.state.user.properties['userId']
        status = Up.status

        if status == '':
            queryToDelete = f"MATCH (n:User {format_properties({'userId': userId})}) REMOVE n.status RETURN n"
            makeQuery(queryToDelete, listOffIndexes=['n'])
            return basicResponse(status='success to update status')

        query = f"MATCH (n:User {format_properties({'userId': userId})}) SET n.status = '{status}' RETURN n"
        makeQuery(query, listOffIndexes=['n'])
        return basicResponse(status='success to update status')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Función para hashear una contraseña y generar una sal
def hash_password(password):
    # Generar una sal aleatoria
    salt = bcrypt.gensalt()
    # Hashear la contraseña con la sal
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password_str = hashed_password.hex()
    return hashed_password_str  # Devuelve el hash como una cadena hexadecimal
