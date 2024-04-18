import io
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, UploadFile

from tools import basicResponse, format_properties, makeQuery, createRelationship, NodeD
from .create import hash_password
csvData = APIRouter()


@csvData.post('/node/', response_model=basicResponse, response_model_exclude_unset=True)
async def upload_node_csv(file: UploadFile, labels: Optional[str] = ''):

    if labels == '':
        baseQuery = "CREATE ( "
    else:
        labels = labels.split(',')
        labels = [label.upper() for label in labels]
        baseQuery = f"CREATE (: {':'.join(labels)} "
    try:
        # Aquí se debe implementar la lógica para leer el archivo CSV y subir los nodos a la base de datos
        # La variable 'file' contiene el archivo CSV que se subió, el cual debemos leer
        # Simular la lectura de bytes como un archivo en memoria
        csv_data = io.BytesIO(file.file.read())

        # Leer el archivo CSV
        df = pd.read_csv(csv_data, index_col=None)
        # Eliminar la columna de índices (es decir, resetear el índice)
        df.reset_index(drop=True, inplace=True)
        query = ''

        if 'password' in df.columns:
            df['password'] = df['password'].apply(lambda x: str(hash_password(x)))

        for nodeProps in df.to_dict(orient='records'):
            query += baseQuery + format_properties(nodeProps) + ')\n'

        if query == '':
            return HTTPException(status_code=400, detail='No data to upload')

        query += "with 0 as n"

        query += 'RETURN n'

        print(query)

        makeQuery(query, listOffIndexes=['n'])

        return basicResponse(status='success to upload node')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@csvData.post('/upload/relation/', response_model=basicResponse, response_model_exclude_unset=True)
async def upload_node_csv(file: UploadFile, typeR: str, labels1: Optional[str] = '', labels2: Optional[str] = ''):
    labels = [labels1.strip().upper().split(','), labels2.strip().upper().split(',')]

    try:
        # Aquí se debe implementar la lógica para leer el archivo CSV y subir los nodos a la base de datos
        # La variable 'file' contiene el archivo CSV que se subió, el cual debemos leer
        # Simular la lectura de bytes como un archivo en memoria
        csv_data = io.BytesIO(file.file.read())

        # Leer el archivo CSV
        df = pd.read_csv(csv_data, index_col=None)
        # Eliminar la columna de índices (es decir, resetear el índice)
        df.reset_index(drop=True, inplace=True)
        query = ''

        elements = df.columns

        for relation in df.to_dict(orient='records'):
            node1 = NodeD(labels=labels[0], properties={elements[0]: relation[elements[0]]})
            node2 = NodeD(labels=labels[1], properties={elements[1]: relation[elements[1]]})
            properties = {key: relation[key] for key in elements[2:]}
            createRelationship(node1, node2, typeR, properties=properties)

        if query == '':
            return HTTPException(status_code=400, detail='No data to upload')

        return basicResponse(status='success to upload node')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


