from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CancionCatalogo(BaseModel):
    id: Optional[int] = Field(default=None, description="ID de la canción")
    artists: str = Field(..., description="Artistas de la canción")
    album_name: str = Field(..., description="Nombre del álbum")
    track_name: str = Field(..., description="Nombre de la pista")
    duration_ms: int = Field(..., description="Duración de la pista en milisegundos")
    track_genre: str = Field(..., description="Género de la pista")
