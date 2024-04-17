from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

from tools import makeQuery, format_properties, searchLIMIT
from tools import node, relationship, searchNodesModel, searchRelationshipsModel, relationShipModel, relationSearch, onlyIdPost
from typing import Dict, Any, List, Optional
from loginUtilities import BearerAuthMiddleware

read = APIRouter()


@read.post('/node', response_model=searchNodesModel, response_model_exclude_unset=True)
async def searchNode(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels

        query = f"MATCH (n{':' if len(labels) > 0 else ''}{':'.join(labels)} {format_properties(properties)}) RETURN n"

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
    try:
        userId = request.state.user.properties['userId']
        prop = {'userId': userId}
        query = f"MATCH (u:User:Person {format_properties(prop)})-[r:AFFILIATE]->(a:User:Organization) RETURN u, r, a"
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

            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.post('/post/', response_model=searchRelationshipsModel, dependencies=[Depends(BearerAuthMiddleware())],
           response_model_exclude_unset=True)
async def searchPost(request: Request):
    try:
        userId = request.state.user.properties['userId']
        query = "MATCH (u:User {userId:'"+userId+"')-[r:POSTED]->(p:Post) RETURN u, r, p"
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
        WHERE type(interaction) IN ['LIKE', 'COMMENTS', 'SAVED']
        WITH u, p, count(interaction) AS strength
        
        // Calcular similitud entre posts basada en las etiquetas y propiedades
        MATCH (p1:Post)-[:TAGS]->(h:Hashtag)<-[:TAGS]-(p2:Post)
        WHERE p1 <> p2
        WITH p1, p2, collect(h.name) AS commonTags, count(*) AS tagOverlap
        MERGE (p1)-[similarity:SIMILAR_TO]->(p2)
        SET similarity.score = tagOverlap
        WITH p1, p2
        
        // Recomendar posts similares y recientes a los que el usuario ha interactuado
        MATCH (u)-[:LIKE|COMMENTS|SAVED]->(p:Post)
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
        query = (f"MATCH (u:User {format_properties({'userId': userId})})"
                 f"-[r:SAVED]->(p:Post)<-[r2:POSTED]->(u2:User) RETURN p,r2,u2")
        results = makeQuery(query, listOffIndexes=['p', 'r2', 'u2'])
        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        relations: List[relationShipModel] = []

        for r in results:
            n = node(labels=r[2].labels, properties=r[2].properties)
            s = node(labels=r[0].labels, properties=r[0].properties)

            relation = relationShipModel(typeR=r[1].type, properties=r[1].properties,
                                         nodeTo=s,
                                         nodeFrom=n)

            relations.append(relation)
        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@read.get('/getAllPosts/')
async def getAllPosts():
    try:
        query = (f"MATCH (u:User)-[r:POSTED]->(p:Post) RETURN u, r, p "
                 f" ORDER BY r.creationDate DESC LIMIT 7")
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


@read.post('/getPost/bySearch/{search}/')
async def getAllPostsBySearch(limits: searchLIMIT):
    try:
        search = limits.search
        skip = limits.skip
        limit = limits.limit
        # Construir la parte principal de la consulta Cypher
        query = "MATCH (p:Post) <-[r:POSTED]- (u:User)"

        # Construir la condición WHERE en función de la búsqueda
        where_conditions = []
        if search:
            where_conditions.append(f"p.textContent CONTAINS '{search.replace("'", r'\\\'')}'")
            where_conditions.append(
                f"(EXISTS {{MATCH (p)-[:TAGS]->(h:Hashtag) WHERE h.name = '{search.replace("'", r'\\\'')}'}})")

        if where_conditions:
            query += " WHERE " + " OR ".join(where_conditions)

        # Agregar el resto de la consulta Cypher
        query += """
        RETURN u,r,p
        ORDER BY r.creationDate DESC
        """

        # Agregar SKIP y LIMIT si se proporcionan valores
        if skip is not None:
            query += f"\nSKIP {skip}"
        if limit is not None:
            query += f"\nLIMIT {limit}"

        # Ejecutar la consulta Cypher y procesar los resultados
        results = makeQuery(query, listOffIndexes=['u', 'r', 'p'])

        relations: List[relationShipModel] = []

        if len(results) == 0:
            return searchRelationshipsModel(status='success', relationships=[])

        for r in results:
            n = node(labels=r[0].labels, properties=r[0].properties)
            s = node(labels=r[2].labels, properties=r[2].properties)

            relation = relationShipModel(typeR=r[1].type, properties=r[1].properties,
                                         nodeTo=s,
                                         nodeFrom=n)

            relations.append(relation)

        return searchRelationshipsModel(status='success', relationships=relations)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@read.post('/relation/', response_model=searchRelationshipsModel, dependencies=[Depends(BearerAuthMiddleware())],
           response_model_exclude_unset=True)
async def searchRelation(request: Request, relationS: relationSearch):
    try:
        userId = request.state.user.properties['userId']
        prop = {'userId': userId}
        query = f"MATCH (u:User {format_properties(prop)})-[r:{relationS.relationType}]->(p{':'if len(relationS.labels) > 0 else ''}{':'.join(relationS.labels)}) RETURN u, r, p"
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


@read.get('/getComments/byPostId/{idPost}/')
async def getCommentsByPostId(idPost: str):
    query = f"MATCH (p:Post {{postId: '{idPost}'}})<-[:RESPONSE_TO]-(u:Comment) RETURN u"
    results = makeQuery(query, listOffIndexes=['u'])
    if len(results) == 0:
        return searchNodesModel(status='success', nodes=[])
    return searchNodesModel(status='success', nodes=[node(**r[0].to_json()) for r in results])


