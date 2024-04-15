from datetime import datetime

from tools import makeQuery, createNode, createRelationship, format_properties, NodeD
from typing import List, Dict, Any
import uuid
import random


def createHashtags(hashtags: List[str], idPost: str):
    print(hashtags)
    for hashtag in hashtags:
        hashtag = hashtag.lower().strip()
        idTag = str(uuid.uuid4())
        order = 1
        if hashtag == '':
            continue
        results = makeQuery(f"MATCH (h:Hashtag {format_properties({"name":hashtag})}) RETURN h", listOffIndexes=['h'])
        if len(results) == 0:
            basicProperties = {
                'name': hashtag,
                'idHashtag': idTag,
                'postCount': 1,
                'creationDate': datetime.date(datetime.now()),
                'engagementRate': random.random() * 100
            }
            createNode(['Hashtag'], basicProperties)

        else:
            basicProperties = results[0][0].properties
            query = f"MATCH (h:Hashtag {format_properties({'name': hashtag})}) SET h.postCount = {basicProperties['postCount']+1} " \
                    "RETURN h"
            tag = makeQuery(query, listOffIndexes=['h'])
            tag = tag[0][0]
            idTag = tag.properties['idHashtag']
            order = tag.properties['postCount']

        createRelationship(NodeD(['Post'], {'postId': idPost}),
                           NodeD(['Hashtag'], {'name': hashtag}), 'TAGS',
                           properties={
                                 'creationDate': datetime.date(datetime.now()),
                                  'idHashtag': idTag,
                               'creationOrder': order
                           })

        query = f"""
        MATCH (h:Hashtag {format_properties({'name': hashtag})})-[:TAGS]->(p:Post)
        WITH h, COUNT(*) AS num_tags, SUM(p.likes) AS total_likes
        SET h.engagement = toFloat(total_likes) / toFloat(num_tags)
        RETURN h.name AS hashtag, num_tags AS cantidad_relaciones, total_likes AS suma_likes, h.engagement AS engagement;
        """
        makeQuery(query, listOffIndexes=['hashtag'])







