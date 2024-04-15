from basics import neo4j_driver
from neo4j import Result
from .Classes import NodeD, transFormObject, format_properties
from typing import List


def createNode(labels: List[str], params=None, merge=False):
    if params is None:
        params = {}

    with neo4j_driver.session() as session:
        cypher_query = f"CREATE (node:{':'.join(labels)} {format_properties(params)})"
        if merge:
            cypher_query = f"MERGE (node:{':'.join(labels)} {format_properties(params)})"
        session.run(cypher_query)


def createRelationship(node1: NodeD, node2: NodeD, typeR: str, properties=None, merge=True):
    if properties is None:
        properties = {}

    with neo4j_driver.session() as session:
        cypher_query = f"MATCH (a{':' if len(node1.labels) > 0 else ''}{':'.join(node1.labels)} " \
                       f"{format_properties(node1.properties)}) " \
                       f"MATCH (b{':' if len(node2.labels) > 0 else ''}{':'.join(node2.labels)}" \
                       f" {format_properties(node2.properties)}) " \
                       f"CREATE (a)-[r:{typeR} {format_properties(properties)}]->(b)"
        if merge:
            cypher_query = f"MATCH (a{':' if len(node1.labels) > 0 else ''}{':'.join(node1.labels)}" \
                           f"{format_properties(node1.properties)}) " \
                           f"MATCH (b{':' if len(node2.labels) > 0 else ''}{':'.join(node2.labels)} " \
                           f"{format_properties(node2.properties)}) " \
                           f"MERGE (a)-[r:{typeR} {format_properties(properties)}]->(b)"
        session.run(cypher_query)


def makeQuery(query: str = 'MATCH (n) RETURN n', params=None, listOffIndexes=None):
    if listOffIndexes is None:
        listOffIndexes = ['n']
    if params is None:
        params = {}

    with neo4j_driver.session() as session:
        nodes: Result = session.run(query, params)
        records = []
        for n in nodes:
            records.append([transFormObject(n[index]) for index in listOffIndexes])
        return records


def searchNode(labels: List[str], properties=None):
    if properties is None:
        properties = {}

    with neo4j_driver.session() as session:
        cypher_query = f"MATCH (node{':' if len(labels) > 0 else ''}{':'.join(labels)} " \
                       f"{format_properties(properties)}) RETURN node"
        nodes = session.run(cypher_query)
        records = []
        for n in nodes:
            records.append(transFormObject(n['node']))
        return records


def detachDeleteNode(properties=None, labels=None):
    if properties is None:
        properties = {}
    with neo4j_driver.session() as session:
        cypher_query = f"MATCH (node{':' if len(labels) > 0 else ''}{':'.join(labels)}" \
                       f" {format_properties(properties)}) DETACH DELETE node"
        session.run(cypher_query)


def deleteNode(properties=None, labels=None):
    if properties is None:
        properties = {}
    with neo4j_driver.session() as session:
        cypher_query = f"MATCH (node{':' if len(labels) > 0 else ''}{':'.join(labels)}" \
                       f" {format_properties(properties)}) DELETE node"
        session.run(cypher_query)


def updateNode(labels: List[str], oldProperties=None, newProperties=None):
    if oldProperties is None:
        oldProperties = {}
    with neo4j_driver.session() as session:
        cypher_query = f"MATCH (node{':' if len(labels) > 0 else ''}{':'.join(labels)}" \
                       f" {format_properties(oldProperties)}) SET node += {format_properties(newProperties)}"
        session.run(cypher_query)


def countLikes(idPost):
    query = f"MATCH (p:Post {{postId: '{idPost}'}})<-[r:LIKE]-()" \
            """
            WITH p, COUNT(r) AS num_relations
            SET p.likes = num_relations
            RETURN n"""
    results = makeQuery(query, listOffIndexes=['likes'])
    return results[0][0]


