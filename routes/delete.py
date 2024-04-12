from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from tools import detachDeleteNode
from tools import node, basicResponse

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
