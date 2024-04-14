from datetime import datetime

from tools import makeQuery, createNode, createRelationship, format_properties
from typing import List, Dict, Any
import uuid


def createHashtags(hashtags: List[str], idPost: str):
    for hashtag in hashtags:
        results = makeQuery(f"MATCH (h:Hashtag {{'name': {hashtag}}}) RETURN h")
        if len(results) == 0:
            basicProperties = {
                'name': hashtag,
                'idHashtag': str(uuid.uuid4()),
                'postCount': 1,
                'creationDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

            }
            createNode(['Hashtag'], {'name': hashtag})







