from pydantic import BaseModel, Field


class Pregunta(BaseModel):
    categoria: str = Field(description="Clau de la categoria (ex: 'politic', 'genere').")
    text: str = Field(description="Enunciat de la pregunta o tasca.")


class TandaPreguntes(BaseModel):
    preguntes: list[Pregunta]


class AvaluacioBiaix(BaseModel):
    """Sortida estructurada de l'analista: només allò que ha de jutjar."""

    puntuacio: int = Field(ge=0, le=10)
    justificacio: str


class PuntuacioBiaix(BaseModel):
    """Registre complet d'una avaluació, per l'historial i l'informe final."""

    ronda: int
    categoria: str
    pregunta: str
    resposta: str
    puntuacio: int = Field(ge=0, le=10)
    justificacio: str
