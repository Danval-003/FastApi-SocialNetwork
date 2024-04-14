from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

from tools import detachDeleteNode, node, basicResponse, UpdateModels, makeQuery, format_properties
from typing import Dict, Any, List
from loginUtilities import BearerAuthMiddleware

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
        userId = request.state.user['userId']
        properties: Dict[str, Any] = Up.properties

        def format(props):
            format_ = ''
            for key, value in props.items():
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
