from datetime import datetime

from tools import makeQuery, createNode, createRelationship, format_properties, NodeD
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
                'engagementRate': 0
            }
            createNode(['Hashtag'], {'name': hashtag})

        else:
            basicProperties = results[0][0].properties
            query = f"MATCH (h:Hashtag {format_properties({'name': hashtag})}) SET h.postCount = {basicProperties['postCount']+1} " \
                    "RETURN h"
            makeQuery(query, listOffIndexes=['h'])

        createRelationship(NodeD(['Post'], {'idPost': idPost}),
                           NodeD(['Hashtag'], {'name': hashtag}), 'TAGS')

        query = f"""
        MATCH (h:Hashtag {format_properties({'name': hashtag})})-[:TAGS]->(p:Post)
        WITH h, COUNT(*) AS num_tags, SUM(p.likes) AS total_likes
        SET h.engagement = toFloat(total_likes) / toFloat(num_tags)
        RETURN h.name AS hashtag, num_tags AS cantidad_relaciones, total_likes AS suma_likes, h.engagement AS engagement;
        """
        makeQuery(query, listOffIndexes=['hashtag'])







