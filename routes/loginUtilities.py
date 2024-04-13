from datetime import timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from basics import create_access_token, oauth2_scheme
from loginUtilities import authenticate_required
from tools import makeQuery, node
import re

loginUtilities = APIRouter()


@loginUtilities.post('/login')
async def login(email: str, password: str):
    query = f"MATCH (u:User {{email: '{email}'}}) RETURN u"
    results = makeQuery(query, listOffIndexes=['u'])
    if len(results) < 0:
        raise HTTPException(status_code=404, detail="User not found")

    user = results[0][0]
    if not verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires
    )

    nodeUser = node(labels=user.labels, properties=user.properties)

    return {"access_token": access_token, "token_type": "bearer", "user": nodeUser}


def verify_password(plain_password, hashed_password_str):
    # Convertir el hash almacenado de vuelta a bytes desde su representación en texto (hexadecimal)
    hashed_password = bytes.fromhex(hashed_password_str)
    # Verificar si la contraseña en texto plano coincide con el hash almacenado
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


@loginUtilities.post('/to_try')
@authenticate_required
async def to_try():
    return {"message": "You are authenticated"}
