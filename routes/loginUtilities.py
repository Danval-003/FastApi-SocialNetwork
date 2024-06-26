from datetime import timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from basics import create_access_token, oauth2_scheme
from loginUtilities import BearerAuthMiddleware
from tools import makeQuery, node, loginModel
from cachetools import cached, TTLCache
import re

loginUtilities = APIRouter()

# Configurar un cache TTL (Time-To-Live) para almacenar las credenciales autenticadas
cache = TTLCache(maxsize=1000, ttl=300)


@loginUtilities.post('/login')
async def login(loginInfo: loginModel):
    try:
        username = loginInfo.username
        password = loginInfo.password
        cached_response = cache.get((username, password))
        if cached_response:
            return cached_response
        query = f"MATCH (u:User {{username: '{username}'}}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) == 0:
            return HTTPException(status_code=404, detail="User not found")

        user = results[0][0]
        if not verify_password(password, user.properties['password']):
            return HTTPException(status_code=401, detail="Incorrect password")

        access_token_expires = timedelta(minutes=300)
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )

        nodeUser = node(labels=user.labels, properties=user.properties)

        response = {"access_token": access_token, "token_type": "bearer", "user": nodeUser}

        cache[(username, password)] = response

        return response
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


def verify_password(plain_password, hashed_password_str):
    # Convertir el hash almacenado de vuelta a bytes desde su representación en texto (hexadecimal)
    hashed_password = bytes.fromhex(hashed_password_str)
    # Verificar si la contraseña en texto plano coincide con el hash almacenado
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


@loginUtilities.post('/to_try', dependencies=[Depends(BearerAuthMiddleware())])
async def to_try(request: Request):
    return {"message": "You are authenticated", "user": request.state.user.dict()}
