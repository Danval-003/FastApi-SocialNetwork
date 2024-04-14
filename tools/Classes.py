from datetime import date
from neo4j import graph


class NodeD:
    def __init__(self, labels, properties):
        self.labels = labels
        self.properties = properties

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_json())


class RelationshipD:
    def __init__(self, type, properties, node1: 'NodeD', node2: 'NodeD'):
        self.type = type
        self.properties = properties
        self.node1 = node1.to_json()
        self.node2 = node2.to_json()

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return f'{self.node1} - {self.type} - {self.node2} ' + str(self.properties)


def format_properties(properties):
    # Formatear las propiedades para la consulta Cypher
    if not properties:
        return ""

    def typed(val):
        if isinstance(val, str):
            return f"'{val.replace('\'', '\\\'')}'"
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, dict):
            return "{" + ", ".join(f"{key}: {typed(value)}" for key, value in val.items()) + "}"
        if isinstance(val, list):
            return "[" + ", ".join(typed(value) for value in val) + "]"
        if isinstance(val, int):
            return str(val)
        if isinstance(val, float):
            return str(val)
        if isinstance(val, date):
            return f"date('{val}')"
        return str(val)

    formatted_props = "{" + ", ".join(f"{key}: {typed(value)}" for key, value in properties.items()) + "}"
    return formatted_props


def transFormObject(obj):
    if isinstance(obj, graph.Node):
        labels = list(obj.labels)
        properties = dict(obj)
        return NodeD(labels, properties)
    elif obj is not None:
        nodesR = [transFormObject(ls) for ls in obj.nodes]
        print(nodesR)
        typeR = obj.type
        properties = dict(obj)
        return RelationshipD(typeR, properties, nodesR[0], nodesR[1])

    return obj
