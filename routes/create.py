import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import bcrypt
from fastapi import APIRouter, HTTPException, UploadFile, Depends, File
from langdetect import detect
from starlette.requests import Request
from werkzeug.utils import secure_filename

from basics import grid_fs, origin
from loginUtilities import BearerAuthMiddleware
from tools import createNode, user_organization, user_person, postNode, affiliate, follow, like
from tools import node, basicResponse, createRelationship, NodeD, relationship, makeQuery, format_properties
from otherOperations import createHashtags

create = APIRouter()


@create.post('/node', response_model=basicResponse)
async def create_node(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels
        merge: bool = N.merge

        createNode(labels, properties, merge)
        response_data = {'status': 'success to create node'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/nodes', response_model=basicResponse, response_model_exclude_unset=True)
async def create_nodes(Ns: List[node]):
    try:
        for N in Ns:
            properties: Dict[str, Any] = N.properties
            labels: List[str] = N.labels
            merge: bool = N.merge

            createNode(labels, properties, merge)
        response_data = {'status': f'success to create {len(Ns)} nodes'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/relationship', response_model=basicResponse, response_model_exclude_unset=True)
async def create_relationship(R: relationship):
    try:
        properties: Dict[str, Any] = R.properties
        type_r: str = R.type
        node1: node = R.node1
        node2: node = R.node2

        createRelationship(typeR=type_r, properties=properties, node1=NodeD(node1.labels, node1.properties),
                           node2=NodeD(node2.labels, node2.properties))
        response_data = {'status': 'success to create relationship'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/user/person/', response_model=basicResponse, response_model_exclude_unset=True)
async def create_user_person(profile_image: UploadFile = File(None), U: user_person = Depends()):
    try:
        query = f"MATCH (u:User:Person {format_properties({"username": U.username})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="User with this username already exists")

        properties: Dict[str, Any] = U.dict()
        labels: List[str] = ['User', 'Person']
        properties['profile_image'] = origin + "multimedia/stream/661995a854e08ee44bee3bda/"
        properties['userId'] = str(uuid.uuid4())
        properties['password'] = hash_password(properties['password'])
        properties['resgisterDate'] = str(datetime.date(datetime.now()))
        properties['mutualCount'] = 0
        properties['followCount'] = 0
        properties['followerCount'] = 0

        if profile_image:
            file_data = await profile_image.read()
            filename = secure_filename(profile_image.filename)
            content_type = profile_image.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['profile_image'] = origin + "multimedia/stream/" + str(file_id) + "/"

        createNode(labels, properties, merge=True)
        response_data = {'status': f'success to create user person with id {properties['userId']}',
                         'id': properties['userId']}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/user/organization', response_model=basicResponse, response_model_exclude_unset=True)
async def create_user_organization(U: user_organization = Depends(), profile_image: UploadFile = File(None)):
    try:
        query = f"MATCH (u:User:Organization {format_properties({'name': U.name})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="Organization with this name already exists")

        properties: Dict[str, Any] = U.dict()
        labels: List[str] = ['User', 'Organization']
        properties['profile_image'] = origin + "multimedia/stream/661995a854e08ee44bee3bda/"
        properties['userId'] = str(uuid.uuid4())
        properties['password'] = hash_password(properties['password'])
        properties['resgisterDate'] = str(datetime.date(datetime.now()))
        properties['followCount'] = 0
        properties['followerCount'] = 0

        if profile_image:
            file_data = await profile_image.read()
            filename = secure_filename(profile_image.filename)
            content_type = profile_image.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['logo_image'] = origin + "multimedia/stream/" + str(file_id) + "/"

        createNode(labels, properties, merge=True)
        response_data = {'status': f'success to create user Organization with id {properties['userId']}',
                         'id': properties['userId']}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/post/', dependencies=[Depends(BearerAuthMiddleware())])
async def makePost(request: Request, P: postNode = Depends(), multimedia: List[UploadFile] = File(None)):
    try:
        userID = request.state.user.properties['userId']
        properties: Dict[str, Any] = P.dict()
        labels: List[str] = ['Post']
        properties['postId'] = str(uuid.uuid4())
        properties['multimedia'] = []
        properties['language'] = detect(properties['textContent'])
        properties['likes'] = 0
        properties['views'] = 0
        properties['hashtags'] = [tag.lower().strip() for tag in P.hashtags.split('#') if tag.lower().strip() != '']

        if multimedia is None:
            multimedia = []

        for media in multimedia:
            file_data = await media.read()
            filename = secure_filename(media.filename)
            content_type = media.content_type

            with grid_fs.new_file(filename=filename, content_type=content_type) as grid_file:
                grid_file.write(file_data)
                file_id = grid_file._id

            properties['multimedia'].append(origin + "multimedia/stream/" + str(file_id) + "/")

        createNode(labels, properties, merge=True)
        createRelationship(typeR='POSTED', properties={}, node1=NodeD(['User'], {'userId': userID}),
                           node2=NodeD(['Post'], {'postId': properties['postId']}))

        createHashtags(P.hashtags.split('#'), properties['postId'])
        response_data = {'status': f'success to create post with id {properties["postId"]}'}

        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/affiliate', dependencies=[Depends(BearerAuthMiddleware())])
async def create_affiliate(request: Request, affiliateData: affiliate):
    try:
        usernameOrganization = affiliateData.usernameOrganization
        role = affiliateData.role
        userId = request.state.user.properties['userId']
        query = f"MATCH (u:User:Person {format_properties({'userId': userId})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="User not found")

        query = f"MATCH (u:User:Organization {format_properties({'username': usernameOrganization})}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Organization not found")

        props = {
            'username': usernameOrganization,
            'affiliatedDate': datetime.date(datetime.now())
        }

        if role is not None:
            props['role'] = role

        createRelationship(typeR='AFFILIATE', properties=props, node1=NodeD(['User'], {'userId': userId}),
                           node2=NodeD(['User'], {'username': usernameOrganization}))
        response_data = {'status': f'success to affiliate user {userId} with organization {usernameOrganization}'}
        return basicResponse(**response_data)

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))



@create.post('/follow', dependencies=[Depends(BearerAuthMiddleware())])
async def follow(request: Request, followData: follow):
    try:
        id_user: str = followData.userId
        userId = request.state.user.properties['userId']
        otherUser = {'userId': id_user}

        query = f"MATCH (u:User {format_properties({'userId': userId})})-[r:FOLLOW]->(o:User {format_properties(otherUser)}) RETURN r"
        results = makeQuery(query, listOffIndexes=['r'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="You already follow this user")

        query = f"MATCH (u:User {format_properties({'userId': userId})})<-[r:FOLLOW]-(o:User {format_properties(otherUser)}) RETURN r"
        results = makeQuery(query, listOffIndexes=['r'])
        mutual = len(results) > 0

        query = f"""
        MATCH (u1:User {format_properties({'userId': userId})})-[:FOLLOW]->(follower1:User)
        MATCH (u2:User {format_properties(otherUser)})-[:FOLLOW]->(follower2:User)
        WITH collect(DISTINCT follower1) AS followersUser1, collect(DISTINCT follower2) AS followersUser2
        WITH [user in followersUser1 WHERE user IN followersUser2] AS commonFollowers
        UNWIND commonFollowers AS commonFollower
        RETURN commonFollower
        """
        results = makeQuery(query, listOffIndexes=['r', 'r2'])

        weight = len(results) + 1

        user = NodeD(['User'], {'userId': userId})
        other = NodeD(['User'], otherUser)

        createRelationship(typeR='FOLLOW', properties={
            'followDate': datetime.date(datetime.now()),
            'isMutual': mutual,
            'weight': weight
        }, node1=user, node2=other)

        if mutual:
            queryToUpdate = f"MATCH (u:User {format_properties(otherUser)})- [r:FOLLOW] -> (o:User {format_properties({'userId': userId})}) "\
                            f"SET r.isMutual = true, r.weight={weight} RETURN r"
            makeQuery(queryToUpdate, listOffIndexes=['r'])

        response_data = {'status': f'success to follow {otherUser}'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@create.post('/like', dependencies=[Depends(BearerAuthMiddleware())])
async def like(request: Request, likeData: like):
    try:
        id_post = likeData.postId
        positive = likeData.positive
        userId = request.state.user.properties['userId']
        post = {'postId': id_post}

        query = f"MATCH(p:Post {format_properties(post)}) RETURN p"
        results = makeQuery(query, listOffIndexes=['p'])
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        query = f"MATCH (u:User {format_properties({'userId': userId})})-[r:LIKE]->(p:Post {format_properties(post)}) RETURN r"
        results = makeQuery(query, listOffIndexes=['r'])
        if len(results) > 0:
            raise HTTPException(status_code=400, detail="You already liked this post")

        query = f"MATCH (u:User)-[r:POSTED]->(p:Post {format_properties(post)}) RETURN u"
        results = makeQuery(query, listOffIndexes=['u'])
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        author = results[0][0]

        authorId = author.properties['userId']
        authorImage = author.properties['profile_image']

        user = NodeD(['User'], {'userId': userId})
        post = NodeD(['Post'], {'postId': id_post})

        createRelationship(typeR='LIKE', properties={
            'likeDate': datetime.date(datetime.now()),
            'authorId': authorId,
            'authorImage': authorImage,
            'positive': positive if positive is not None else True
        }, node1=user, node2=post)

        response_data = {'status': f'success to like post {id_post}'}
        return basicResponse(**response_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


# Función para hashear una contraseña y generar una sal
def hash_password(password):
    # Generar una sal aleatoria
    salt = bcrypt.gensalt()
    # Hashear la contraseña con la sal
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password_str = hashed_password.hex()
    return hashed_password_str  # Devuelve el hash como una cadena hexadecimal
