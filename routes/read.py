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
        query = f"MATCH (u:User:Person {format_properties(prop)})-[r:AFFILIATE]->(a:User:Organization) RETURN u, r, a"
        print(query)
        results = makeQuery(query, listOffIndexes=['u', 'r', 'a'])

        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        relations: List[relationShipModel] = []

        for r in results:
            n = node(labels=r[0].labels, properties=r[0].properties)
            s = node(labels=r[2].labels, properties=r[2].properties)

            relation = relationShipModel(typeR=r[1].type, properties=r[1].properties,
                                         nodeTo=s,
                                         nodeFrom=n)

            print(relation)
            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/post/', response_model=searchRelationshipsModel, dependencies=[Depends(BearerAuthMiddleware())],
           response_model_exclude_unset=True)
async def searchPost(request: Request):
    try:
        userId = request.state.user.properties['userId']
        prop = {'userId': userId}
        query = f"MATCH (u:User {format_properties(prop)})-[r:POSTED]->(p:Post) RETURN u, r, p"
        results = makeQuery(query, listOffIndexes=['u', 'r', 'p'])

        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        relations: List[relationShipModel] = []

        for r in results:
            n = node(labels=r[0].labels, properties=r[0].properties)
            s = node(labels=r[2].labels, properties=r[2].properties)

            relation = relationShipModel(typeR=r[1].type, properties=r[1].properties,
                                         nodeTo=s,
                                         nodeFrom=n)

            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/recommend/post', dependencies=[Depends(BearerAuthMiddleware())])
async def recommendPost(request: Request):
    try:
        userId = request.state.user.properties['userId']
        query = f"""
        // Obtener interacciones de un usuario específico
        MATCH (u:User {format_properties({'userId': userId})})-[interaction]->(p:Post)
        WHERE type(interaction) IN ['LIKES', 'COMMENTS', 'SAVES']
        WITH u, p, count(interaction) AS strength
        
        // Calcular similitud entre posts basada en las etiquetas y propiedades
        MATCH (p1:Post)-[:TAGS]->(h:Hashtag)<-[:TAGS]-(p2:Post)
        WHERE p1 <> p2
        WITH p1, p2, collect(h.name) AS commonTags, count(*) AS tagOverlap
        MERGE (p1)-[similarity:SIMILAR_TO]->(p2)
        SET similarity.score = tagOverlap
        WITH p1, p2
        
        // Recomendar posts similares y recientes a los que el usuario ha interactuado
        MATCH (u)-[:LIKES|COMMENTS|SAVES]->(p:Post)
        WITH u, p
        MATCH (p)-[:SIMILAR_TO]->(recommended:Post)
        WHERE NOT (u)-[:LIKES|COMMENTS|SAVES]->(recommended) 
        RETURN recommended
        LIMIT 10
        """
        results = makeQuery(query, listOffIndexes=['recommended'])

        return searchNodesModel(status='success', nodes=[node(**r[0].to_json()) for r in results])

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/mylikes/', dependencies=[Depends(BearerAuthMiddleware())])
async def myLikes(request: Request):
    try:
        userId = request.state.user.properties['userId']
        query = f"MATCH (u:User {format_properties({'userId': userId})})-[r:LIKE]->(p:Post) RETURN p"
        results = makeQuery(query, listOffIndexes=['p'])
        if len(results) == 0:
            return searchNodesModel(status='success', nodes=[])

        return searchNodesModel(status='success', nodes=[node(**r[0].to_json()) for r in results])

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/mysaves/', dependencies=[Depends(BearerAuthMiddleware())])
async def mySaves(request: Request):
    try:
        userId = request.state.user.properties['userId']
        query = f"MATCH (u:User {format_properties({'userId': userId})})-[r:SAVED]->(p:Post) RETURN p"
        results = makeQuery(query, listOffIndexes=['p'])
        if len(results) == 0:
            return searchNodesModel(status='success', nodes=[])

        return searchNodesModel(status='success', nodes=[node(**r[0].to_json()) for r in results])

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.get('/getAllPosts/')
async def getAllPosts():
    try:
        query = f"MATCH (u:User)-[r:POSTED]->(p:Post) RETURN u, r, p LIMIT 30"
        results = makeQuery(query, listOffIndexes=['u', 'r', 'p'])
        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        relations: List[relationShipModel] = []

        for r in results:
            n = node(labels=r[0].labels, properties=r[0].properties)
            s = node(labels=r[2].labels, properties=r[2].properties)

            relation = relationShipModel(typeR=r[1].type, properties=r[1].properties,
                                         nodeTo=s,
                                         nodeFrom=n)

            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.get('/getPost/bySearch/{search}/{skip}/{limit}')
async def getAllPosts(search: str, skip: int = 0, limit: int = 10):
    try:
        query = f"""
        MATCH (p:Post)
        WHERE p.textContent CONTAINS '{search.replace("'", r"\'")}' OR
              (EXISTS {{MATCH (p)-[:TAGS]->(h:Hashtag) WHERE h.name = '{search.replace("'", r"\'")}'}})
        RETURN p
        ORDER BY p.createDate
        SKIP {skip}  // Saltar los primeros 10 resultados (0-indexed, por lo tanto, 9 para empezar desde el décimo)
        LIMIT {limit}
        """
        results = makeQuery(query, listOffIndexes=['p'])
        if len(results) == 0:
            return searchNodesModel(status='success', nodes=[])

        return searchNodesModel(status='success', nodes=[node(**r[0].to_json()) for r in results])

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
