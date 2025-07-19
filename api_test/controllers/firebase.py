import os
import json
import logging
import firebase_admin
import requests

from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from dotenv import load_dotenv
import asyncpg


from utils.database import execute_query_json
from utils.security import create_jwt_token
from models.Userregister import UserRegister
from models.Userlogin import UserLogin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cred = credentials.Certificate("secrets/firebase_admin.json")
firebase_admin.initialize_app(cred)

load_dotenv()

async def register_user_firebase(user: UserRegister) -> dict:
    clean_email = user.email.strip().lower()
    clean_first_name = user.first_name.strip()
    clean_last_name = user.last_name.strip()

    try:
        user_record = firebase_auth.create_user(
            email=clean_email,
            password=user.password
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )
    except Exception as e:
        logger.error(f"Error en Firebase: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error al registrar usuario en Firebase"
        )

    query = """
        INSERT INTO canciones.users 
            (email, first_name, last_name, active) 
        VALUES (%s, %s, %s, %s)
        RETURNING id, email, first_name, last_name, active, admin
    """
    params = (
        clean_email,
        clean_first_name,
        clean_last_name,
        user.active if user.active is not None else True
    )

    try:
        result_json = await execute_query_json(query, params, needs_commit=True)
        result_dict = json.loads(result_json)
        
        if not result_dict:
            raise Exception("No se recibieron datos de la inserción")

        return {
            "id": result_dict[0]["id"],
            "email": result_dict[0]["email"],
            "first_name": result_dict[0]["first_name"],
            "last_name": result_dict[0]["last_name"],
            "active": result_dict[0]["active"],
            "admin": result_dict[0]["admin"]
        }

    except asyncpg.UniqueViolationError:
        await firebase_auth.delete_user(user_record.uid)
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )
    except Exception as e:
        await firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error en PostgreSQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al registrar usuario en la base de datos"
        )
    
async def login_user_firebase(user: UserLogin) -> dict:
    
    clean_email = user.email.strip().lower()

    
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Configuración de Firebase no encontrada"
        )

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": clean_email,
        "password": user.password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        
        if "error" in response_data:
            raise HTTPException(
                status_code=400,
                detail=response_data['error']['message']
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la solicitud a Firebase: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error al conectar con el servicio de autenticación"
        )

    query = """
        SELECT
            email,
            first_name,
            last_name,
            active,
            admin
        FROM canciones.users
        WHERE email = %s
    """

    try:
        result_json = await execute_query_json(query, (clean_email,), needs_commit=False)
        result_dict = json.loads(result_json)
        
        if not result_dict:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado en la base de datos"
            )

        user_data = result_dict[0]
        return {
            "access_token": create_jwt_token(
                firstname=user_data["first_name"],
                lastname=user_data["last_name"],
                email=clean_email,
                active=user_data["active"],
                admin=user_data["admin"]
            ),
            "token_type": "bearer",
            "user_info": {
                "email": clean_email,
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "admin": user_data["admin"]
            }
        }
    except Exception as e:
        logger.error(f"Error en la base de datos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )