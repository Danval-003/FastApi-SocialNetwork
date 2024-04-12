from fastapi import APIRouter, HTTPException
from tools import makeQuery, format_properties
from tools import node, relationship, searchNodesModel
from typing import Dict, Any, List


read = APIRouter()


@read.post('/node', response_model=searchNodesModel, response_model_exclude_unset=True)
async def searchNode(N: node):
    try:
        properties: Dict[str, Any] = N.properties
        labels: List[str] = N.labels

        query = f"MATCH (n:{':'.join(labels)} {format_properties(properties)}) RETURN n"

        results = makeQuery(query, listOffIndexes=['n'])

        nodes = [node(**n[0].to_json()) for n in results]

        return searchNodesModel(status='success', nodes=nodes)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
