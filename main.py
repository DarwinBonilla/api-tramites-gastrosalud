"""
main.py - API REST de Trámites Clínicos — Centro Médico GastroSalud Cía. Ltda.
Taller 3 - Gestión de Servicios en la Nube (UBE - Grupo 1).

Ejecutar:                                     uvicorn main:app --reload
Documentación interactiva (Swagger UI):       http://localhost:8000/docs
Contrato OpenAPI:                             http://localhost:8000/openapi.json
"""

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

import datos
from seguridad import autenticar_usuario, crear_token, obtener_usuario_actual

app = FastAPI(
    title="API de Trámites Clínicos — Centro Médico GastroSalud",
    version="1.0.0",
    description=(
        "API RESTful que expone de forma segura y controlada el servicio de consulta "
        "y solicitud de trámites médico-administrativos (autorizaciones de EDA, "
        "colonoscopias, informes firmados y certificados) del sistema heredado "
        "Linux/MySQL del Centro Médico de Especialidades Gastroenterológicas del "
        "Ecuador (GastroSalud Cía. Ltda.). Cumple con LOPDP (2021) y el Acuerdo "
        "Ministerial 5216 del MSP. Elaborado por el Grupo 1 (UBE)."
    ),
)


# ------------------------- Modelos (esquemas DTO) -------------------------
# Definen qué datos entran y salen. FastAPI los usa para validar y para
# generar el contrato OpenAPI automáticamente.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TramiteNuevo(BaseModel):
    tipo: str = Field(
        ...,
        min_length=3,
        max_length=120,
        examples=["Solicitud de Informe Firmado de Endoscopia Digestiva Alta (EDA)"],
    )
    especialidad: str = Field(
        default="Gastroenterología Clínica",
        min_length=3,
        max_length=80,
        examples=["Gastroenterología Clínica"],
    )


class Tramite(BaseModel):
    id: int
    tipo: str
    especialidad: str = "Gastroenterología Clínica"
    estado: str
    fecha: date
    # Nota de Seguridad y Privacidad (LOPDP / MSP 5216):
    # Los campos internos "propietario", "historia_clinica_interna",
    # "cie10_confidencial" y "factura_php_id" NO se declaran en este esquema
    # de salida, garantizando que jamás se filtren hacia los consumidores.


# ------------------------------ Endpoints ---------------------------------
@app.get("/", tags=["Estado"])
def estado_servicio():
    """Verifica que la API de GastroSalud está en línea (health check para Azure Application Gateway / AKS)."""
    return {
        "servicio": "API de Trámites Clínicos — Centro Médico GastroSalud",
        "organizacion": "Centro Médico de Especialidades Gastroenterológicas del Ecuador",
        "estado": "en línea",
    }


@app.post("/api/v1/token", response_model=Token, tags=["Autenticación"])
def obtener_token(formulario: OAuth2PasswordRequestForm = Depends()):
    """Recibe usuario y contraseña del paciente y devuelve un token JWT firmado (HS256)."""
    usuario = autenticar_usuario(formulario.username, formulario.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=crear_token(usuario["usuario"]))


@app.get("/api/v1/tramites", response_model=list[Tramite], tags=["Trámites"])
def listar_tramites(usuario=Depends(obtener_usuario_actual)):
    """Lista los trámites clínico-administrativos del paciente autenticado."""
    return datos.listar_tramites(usuario["usuario"])


@app.get(
    "/api/v1/tramites/{tramite_id}",
    response_model=Tramite,
    tags=["Trámites"],
    responses={404: {"description": "Trámite no encontrado"}},
)
def consultar_tramite(tramite_id: int, usuario=Depends(obtener_usuario_actual)):
    """Consulta el estado de un trámite clínico del paciente autenticado."""
    tramite = datos.buscar_tramite(tramite_id)
    # Si el trámite no existe o pertenece a otro paciente se responde 404,
    # para no revelar información clínica de terceros (mitigación BOLA / IDOR).
    if tramite is None or tramite["propietario"] != usuario["usuario"]:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return tramite


@app.post(
    "/api/v1/tramites",
    response_model=Tramite,
    status_code=status.HTTP_201_CREATED,
    tags=["Trámites"],
)
def registrar_tramite(nuevo: TramiteNuevo, usuario=Depends(obtener_usuario_actual)):
    """Registra una nueva solicitud de trámite clínico a nombre del paciente autenticado."""
    return datos.registrar_tramite(
        nuevo.tipo, usuario["usuario"], nuevo.especialidad
    )
