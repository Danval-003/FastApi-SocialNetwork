from typing import Callable

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from basics import oauth2_scheme, SECRET_KEY, ALGORITHM
from tools import makeQuery, node
from warnings import warn


def get_user(username: str):
    query = f"MATCH (u:User {{username: '{username}'}}) RETURN u"
    results = makeQuery(query, listOffIndexes=['u'])
    if len(results) != 1:
        return None
    return node(labels=results[0][0].labels, properties=results[0][0].properties)


class BearerAuthMiddleware(HTTPBearer):
    async def __call__(self, request: Request):
        try:
            token = await oauth2_scheme.__call__(request)
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    raise HTTPException(status_code=401, detail="Invalid token")
                user = get_user(username)
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")
                request.state.user = user  # Almacenar el usuario autenticado en el estado de la solicitud
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token has expired")
            except jwt.PyJWTError:
                raise HTTPException(status_code=401, detail="Invalid token")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
