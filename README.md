# FastApi-SocialNetwork

Este proyecto es una red social desarrollada con FastAPI, un moderno y rápido (de alto rendimiento) framework web para construir APIs con Python 3.7+ basado en estándares Python type hints.

## Características

- **Rápido**: Alto rendimiento, a la par con NodeJS y Go (gracias a Starlette y Pydantic). Uno de los frameworks más rápidos disponibles.
- **Fácil de usar**: Diseñado para ser fácil de usar y aprender. Menos tiempo leyendo documentación y más tiempo produciendo código.
- **Robusto**: Proporciona seguridad de tipo de clase mundial. Basado en y completamente compatible con los estándares de Python type hints.
- **Basado en estándares**: Basado en (y completamente compatible con) los estándares de la API abierta (anteriormente conocido como Swagger) y JSON Schema.

## Requisitos

- Python 3.7+
- FastAPI
- Uvicorn: un servidor ASGI ligero para ejecutar FastAPI

## Instalación

Primero, asegúrate de tener Python 3.7+ instalado. Luego, instala las dependencias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Ejecución

Para ejecutar el servidor, usa el siguiente comando:

```bash
uvicorn main:app --reload
```

El flag `--reload` hace que el servidor se reinicie después de cambios en el código. Útil para desarrollo.

## Estructura del Proyecto

- `main.py`: El archivo principal que inicia la aplicación FastAPI.
- `/rutas`: Directorio para los archivos de rutas de la aplicación.
- `/modelos`: Directorio para los modelos de la base de datos.
- `/schemas`: Directorio para los esquemas de Pydantic que definen la estructura de los datos para las solicitudes y respuestas.

## Endpoints

### Crear

- **`POST /create/node`**: Crea un nodo.
- **`POST /create/nodes`**: Crea múltiples nodos.
- **`POST /create/relationship`**: Crea una relación.
- **`POST /create/user/person`**: Crea un usuario persona.
- **`POST /create/user/organization`**: Crea un usuario organización.
- **`POST /create/post`**: Crea un post.
- **`POST /create/affiliate`**: Crea un afiliado.
- **`POST /create/follow`**: Seguir a un usuario.
- **`POST /create/like`**: Dar me gusta a un post.
- **`POST /create/saves`**: Guardar un post.
- **`POST /create/comments`**: Crear un comentario.
- **`POST /create/setMemberStatus`**: Establecer el estado de un miembro.

### Eliminar

- **`POST /delete/node/detach`**: Eliminar un nodo.
- **`POST /delete/relation/post`**: Eliminar una relación (like).
- **`POST /delete/delete/post`**: Eliminar un post.
- **`POST /delete/delete/follow`**: Dejar de seguir a un usuario.
- **`POST /delete/delete/saves`**: Eliminar un post guardado.

### Buscar

- **`POST /search/node`**: Buscar nodo.
- **`POST /search/user/person`**: Buscar usuario persona.
- **`POST /search/user/organization`**: Buscar usuario organización.
- **`POST /search/affiliate`**: Buscar afiliado.
- **`POST /search/post`**: Buscar post.
- **`POST /search/recommend/post`**: Recomendar post.
- **`POST /search/mylikes`**: Buscar mis likes.
- **`POST /search/mysaves`**: Buscar mis guardados.
- **`GET /search/getAllPosts`**: Obtener todos los posts.
- **`POST /search/getPost/bySearch/{search}`**: Buscar posts por término de búsqueda.
- **`POST /search/relation`**: Buscar relación.
- **`GET /search/getComments/byPostId/{idPost}`**: Obtener comentarios por ID de post.
- **`GET /search/bestHashtags`**: Obtener los mejores hashtags.

### Actualizar

- **`POST /update/node`**: Actualizar nodo.
- **`POST /update/user`**: Actualizar usuario.
- **`POST /update/user/profileImage`**: Actualizar imagen de perfil.
- **`POST /update/user/affiliate`**: Actualizar afiliado de usuario.
- **`POST /update/status`**: Actualizar estado.
- **`POST /update/status/post`**: Actualizar estado de post.

### Multimedia

- **`POST /multimedia/upload`**: Subir multimedia.

## Contribuir

Las contribuciones son lo que hace que la comunidad de código abierto sea un lugar increíble para aprender, inspirar y crear. Cualquier contribución que hagas será muy apreciada.

1. Haz un Fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Realiza tus cambios y haz commit (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## Contacto

Twitter - [@Danvalak_14](https://x.com/Danvalak_14)

Email - danarvare2003@gmail.com

Proyecto Link: [https://github.com/Danval-003/FastApi-SocialNetwork](https://github.com/Danval-003/FastApi-SocialNetwork)
