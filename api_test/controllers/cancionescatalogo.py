import json
import logging
from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from models.cancionescatalogo import CancionCatalogo

logger = logging.getLogger(__name__)

CANCIONES_CACHE_KEY="canciones:catalog:all"
CACHE_TTL = 1800

async def get_cancion_catalogo() -> list[CancionCatalogo]:
    
    redis_client = get_redis_client()
    cache_data = get_from_cache(redis_client, CANCIONES_CACHE_KEY)
    if cache_data:
        return [CancionCatalogo(**item) for item in cache_data]

    query = "SELECT * FROM canciones.catalogos;"
    results = await execute_query_json(query)
    dict = json.loads(results)
    if not dict:
        raise HTTPException(status_code=404, detail="No se encontraron canciones en el catálogo.")
    
    return [CancionCatalogo(**item) for item in dict]

async def get_canciones_by_genre(track_genre: str) -> list[CancionCatalogo]:

    redis_client = get_redis_client()
    cache_data = get_from_cache(redis_client, CANCIONES_CACHE_KEY)
    if cache_data:
        return [CancionCatalogo(**item) for item in cache_data]

    query = """
        SELECT * 
        FROM canciones.catalogos 
        WHERE LOWER(track_genre) = LOWER(%s)
        Limit 100
    """
    params = (track_genre.strip(),)
    
    try:
        results_json = await execute_query_json(query, params, needs_commit=False)
        songs_dict = json.loads(results_json)
        
        if not songs_dict:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron canciones en el género '{track_genre}'"
            )
        
        return [CancionCatalogo(**item) for item in songs_dict]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al consultar la base de datos"
        )
    
async def create_cancion(cancion_data: CancionCatalogo) -> CancionCatalogo:
    
    max_id_query = "SELECT COALESCE(MAX(id), 0) AS max_id FROM canciones.catalogos"
    max_id_result = await execute_query_json(max_id_query)
    max_id_data = json.loads(max_id_result)
    
    if not max_id_data or len(max_id_data) == 0:
        raise HTTPException(
            status_code=500,
            detail="Error al conectar con la base de datos"
        )

    current_max_id = int(max_id_data[0].get('max_id', 0))  # Convertir a entero
    new_id = current_max_id + 1

    # Query para insertar la nueva canción
    insert_query = """
        INSERT INTO canciones.catalogos(
            id,
            artists,
            album_name,
            track_name,
            duration_ms,
            track_genre
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
        RETURNING id, artists, album_name, track_name, duration_ms, track_genre
    """

    params = (
        new_id,
        cancion_data.artists,
        cancion_data.album_name,
        cancion_data.track_name,
        cancion_data.duration_ms,
        cancion_data.track_genre
    )

    try:
        # Ejecutar la inserción
        insert_result = await execute_query_json(insert_query, params, needs_commit=True)
        inserted_data = json.loads(insert_result)
        
        if not inserted_data:
            raise HTTPException(
                status_code=500,
                detail="Error al crear la canción en la base de datos"
            )

        # Crear el objeto de respuesta
        created_cancion = CancionCatalogo(
            id=new_id,
            artists=cancion_data.artists,
            album_name=cancion_data.album_name,
            track_name=cancion_data.track_name,
            duration_ms=cancion_data.duration_ms,
            track_genre=cancion_data.track_genre
        )

        redis_client = get_redis_client()
        cache_deleted = delete_cache( redis_client, CANCIONES_CACHE_KEY )

        return created_cancion

    except Exception as e:
        logger.error(f"Error al crear canción: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )