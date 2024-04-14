from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

from tools import makeQuery, format_properties
from tools import node, relationship, searchNodesModel, searchRelationshipsModel, relationShipModel
from typing import Dict, Any, List
from loginUtilities import BearerAuthMiddleware

read = APIRouter()


@read.post('/node', response_model=searchNodesModel, response_model_exclude_unset=True)
async def searchNode(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels

        query = f"MATCH (n{':' if len(labels) > 0 else ''}{':'.join(labels)} {format_properties(properties)}) RETURN n"

        print(query)

        results = makeQuery(query, listOffIndexes=['n'])

        nodes = [node(**n[0].to_json()) for n in results]

        return searchNodesModel(status='success', nodes=nodes)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/user/person', response_model=searchNodesModel, response_model_exclude_unset=True)
async def searchUserPerson(properties: Dict[str, Any]):
    try:
        query = f"MATCH (u:User:Person {format_properties(properties)}) RETURN u"

        results = makeQuery(query, listOffIndexes=['u'])

        nodes = [node(labels=n[0].labels, properties=n[0].properties) for n in results]

        return searchNodesModel(status='success', nodes=nodes)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/user/organization', response_model=searchNodesModel, response_model_exclude_unset=True)
async def searchUserPerson(properties: Dict[str, Any]):
    try:
        query = f"MATCH (u:User:Organization {format_properties(properties)}) RETURN u"

        results = makeQuery(query, listOffIndexes=['u'])

        nodes = [node(labels=n[0].labels, properties=n[0].properties) for n in results]

        return searchNodesModel(status='success', nodes=nodes)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/affiliate', dependencies=[Depends(BearerAuthMiddleware())], response_model=searchRelationshipsModel,
           response_model_exclude_unset=True)
async def searchAffiliate(request: Request):
    print("DADSASDA")
    try:
        userId = request.state.user.properties['userId']
        print("User ID: ", userId)
        prop = {'userId': userId}
        query = f"MATCH (u:User:Person {format_properties(prop)})-[r:AFFILIATE]-(a:User:Organization) RETURN r"
        print(query)
        results = makeQuery(query, listOffIndexes=['r'])

        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        relations: List[relationShipModel] = []

        for r in results:
            print(r[0].to_json())
            relation = relationShipModel(type=r[0].type, properties=r[0].properties,
                                         nodeTo=node(labels=r[0].node1["labels"],
                                                     properties=r[0].node1["properties"]),
                                         nodeFrom=node(labels=r[0].node2["labels"], properties=r[0].node2["properties"]))
            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
