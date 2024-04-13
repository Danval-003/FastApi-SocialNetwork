import jwt
from fastapi import HTTPException, Request
from starlette import status

from basics import oauth2_scheme, SECRET_KEY, ALGORITHM
from tools import makeQuery, node


def get_user(email: str):
    query = f"MATCH (u:User:Person {{email: '{email}'}}) RETURN u"
    results = makeQuery(query, listOffIndexes=['u'])
    if len(results) < 0:
        return None
    return node(labels=results[0][0].labels, properties=results[0][0].properties)


# Decorador para requerir autenticación
def authenticate_required(func):
    async def wrapper(request: Request):
        try:
            token = await oauth2_scheme.__call__(request)
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email: str = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                user = get_user(email)
                if not user:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
            except jwt.PyJWTError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

            # Almacenar el objeto de usuario autenticado en la solicitud
            request.state.user = user

            # Llamar a la función decorada con el objeto de usuario autenticado
            return await func(request)
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))

    return wrapper

