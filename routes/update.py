from fastapi import APIRouter, HTTPException
from tools import detachDeleteNode, node, basicResponse
from typing import Dict, Any, List

update = APIRouter()


@update.post('/node', response_model=basicResponse, response_model_exclude_unset=True)
async def update_node(N: node):
    properties: Dict[str, Any] = N.properties
    labels: List[str] = N.labels
    detachDeleteNode(properties, labels)

    return basicResponse(status='success to update node')

