from typing import Dict, Any, List

from starlette.requests import Request

from basics import neo4j_driver
from loginUtilities import BearerAuthMiddleware
from fastapi import APIRouter, HTTPException, Depends
from tools import detachDeleteNode, makeQuery, countLikes
from tools import node, basicResponse, relationPost, format_properties, follow

delete = APIRouter()


@delete.post('/node/detach', response_model=basicResponse, response_model_exclude_unset=True)
async def delete_node(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels
        detachDeleteNode(properties, labels)

        return basicResponse(status='success to delete node')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@delete.post('/relation/post/', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def delete_like(postInfo: relationPost, request: Request):
    try:
        query = f"MATCH (p:Post {{postId: '{postInfo.idPost}'}}) RETURN p"
        results = makeQuery(query, listOffIndexes=['p'])
        if len(results) == 0:
            return HTTPException(status_code=404, detail="Post not found")
        userID = request.state.user.properties['userId']
        query = (f"MATCH (u:User {format_properties({'userId': userID})})-[l:LIKE]->(p:Post "
                 f"{format_properties({'postId': postInfo.idPost})}) RETURN l")

        results = makeQuery(query, listOffIndexes=['l'])
        if len(results) == 0:
            return HTTPException(status_code=404, detail="Relation not found")
        query = f"MATCH (u:User {{userId: '{userID}'}})-[l:{postInfo.relationType}]->(p:Post {{postId: '{postInfo.idPost}'}}) DELETE l"
        with neo4j_driver.session() as session:
            session.run(query)

        countLikes(postInfo.idPost)
        return basicResponse(status='success to delete like')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@delete.post('/delete/post', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def delete_post(request: Request):
    try:
        userID = request.state.user.properties['userId']
        query = f"MATCH (u:User {{userId: '{userID}'}})-[l:POSTED]->(p:Post) DETACH DELETE p"
        with neo4j_driver.session() as session:
            session.run(query)

        return basicResponse(status='success to delete like')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@delete.post('/delete/follow', response_model=basicResponse, response_model_exclude_unset=True,
             dependencies=[Depends(BearerAuthMiddleware())])
async def delete_follow(request: Request, followData: follow):
    try:
        otherUserID = followData.username
        userID = request.state.user.properties['userId']
        query = f"MATCH (u:User {{userId: '{userID}'}})-[l:FOLLOW]->(u:User {format_properties({'username': otherUserID})}) DETACH DELETE l"
        with neo4j_driver.session() as session:
            session.run(query)

        return basicResponse(status='success to delete like')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
