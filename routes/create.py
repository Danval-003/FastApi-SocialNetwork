from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from tools import node, basicResponse

from tools import createNode

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
