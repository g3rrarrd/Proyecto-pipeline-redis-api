from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import pool
import logging
import json
from typing import Optional, Union, List, Dict

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de la conexión
port = os.getenv('PGPORT')
sslmode = os.getenv('SSLMODE')
server = os.getenv('PGHOST')
database = os.getenv('PGDATABASE')
username = os.getenv('PGUSER')
password = os.getenv('PGPASSWORD')

# Pool de conexiones
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    host=server,
    port=port,
    dbname=database,
    user=username,
    password=password,
    sslmode=sslmode
)

async def get_db_connection():
    try:
        logger.info("Intentando conectar a la base de datos...")
        conn = connection_pool.getconn()
        logger.info("Conexión exitosa a la base de datos")
        return conn
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        raise

async def execute_query_json(sql_template: str, params: Optional[tuple] = None, needs_commit: bool = False) -> Union[str, List[Dict]]:
    conn = None
    cursor = None
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        param_info = "(sin parámetros)" if not params else f"(con {len(params)} parámetros)"
        logger.info(f"Ejecutando consulta {param_info}: {sql_template}")

        if params:
            cursor.execute(sql_template, params)
        else:
            cursor.execute(sql_template)

        results = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            logger.info(f"Columnas obtenidas: {columns}")
            for row in cursor.fetchall():
                # Convertir tipos especiales como UUID, date, etc. a string
                processed_row = [
                    str(item) if item is not None else None 
                    for item in row
                ]
                results.append(dict(zip(columns, processed_row)))

        if needs_commit:
            logger.info("Realizando commit de la transacción.")
            conn.commit()

        return json.dumps(results, default=str, ensure_ascii=False)

    except psycopg2.Error as e:
        logger.error(f"Error ejecutando la consulta (SQLSTATE: {e.pgcode}): {e.pgerror}")
        if conn and needs_commit:
            try:
                logger.warning("Realizando rollback debido a error.")
                conn.rollback()
            except psycopg2.Error as rb_e:
                logger.error(f"Error durante el rollback: {rb_e}")
        raise Exception(f"Error ejecutando consulta: {str(e)}") from e

    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución de la consulta: {str(e)}")
        raise 

    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)
            logger.info("Conexión devuelta al pool.")