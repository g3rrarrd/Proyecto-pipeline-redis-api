from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class UserRegister(BaseModel):
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email del usuario, debe ser un correo electrónico válido."
    )

    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña del usuario, debe tener entre 8 y 64 caracteres incluir por lo menos un numero, por lo menos una mayuscula y por lo menos un caracter especial."
    )

    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="Nombre del usuario, debe tener entre 1 y 50 caracteres.",
        pattern=r"^[a-zA-ZÀ-ÿ\s]+$"
    )

    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="Apellido del usuario, debe tener entre 1 y 50 caracteres.",
        pattern=r"^[a-zA-ZÀ-ÿ\s]+$"
    )

    active: Optional[bool] = Field(
        default=True,
        description="Indica si el usuario está activo. Por defecto es True."
    )
