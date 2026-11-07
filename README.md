# API de Trámites Clínicos — Centro Médico GastroSalud (Taller 3)

**Gestión de Servicios en la Nube · Unidad 3 · Maestría en Gestión de Sistemas y Tecnologías de la Información (UBE)**  
**Docente:** Ing. Alfonso Aníbal Guijarro Rodríguez  
**Grupo 1:** David Usiña · Mariuxi León · Darwin Bonilla · Patricio Jarrín

API RESTful construida con **FastAPI (Python)** que expone de manera controlada y segura el servicio de consulta y solicitud de trámites médico-administrativos (autorizaciones de Endoscopia Digestiva Alta - EDA, entregas de informes firmados de Colonoscopia y certificados médicos) del sistema heredado Linux/MySQL del **Centro Médico de Especialidades Gastroenterológicas del Ecuador (GastroSalud Cía. Ltda.)**, protegiendo los datos clínicos sensibles conforme a la **LOPDP (2021)** y al **Acuerdo Ministerial 5216 del MSP (2014)**.

Incluye contrato **OpenAPI 3.1 (`openapi.json`)**, autenticación basada en tokens **JWT (HS256 + PBKDF2-SHA256)**, suite de **8 pruebas automatizadas con `pytest`** y pipeline de Integración Continua en **GitHub Actions (`.github/workflows/ci.yml`)**.

## Ejecutar en local

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

- **Documentación Interactiva (Swagger UI):** http://localhost:8000/docs
- **Contrato OpenAPI (JSON):** http://localhost:8000/openapi.json

Usuarios de prueba (Pacientes del Portal GastroSalud): `ana / ana123` y `luis / luis123`.

## Ejecutar las pruebas automatizadas

```bash
pytest -v
```

## Contrato de Endpoints REST

| Método | Ruta | Descripción | Respuesta | Protegido (JWT) |
| :---: | :--- | :--- | :--- | :---: |
| `GET` | `/` | Verifica el estado de salud del servicio (*Health Check* para Azure App Gateway / AKS) | `200 OK` | No |
| `POST` | `/api/v1/token` | Autentica al paciente con usuario y contraseña y emite un token JWT | `200 OK` / `401` | No |
| `GET` | `/api/v1/tramites` | Lista los trámites clínico-administrativos del paciente autenticado | `200 OK` / `401` | Sí |
| `GET` | `/api/v1/tramites/{tramite_id}` | Consulta el estado de un trámite específico del paciente | `200 OK` / `401` / `404` | Sí |
| `POST` | `/api/v1/tramites` | Registra una nueva solicitud de trámite clínico | `201 Created` / `401` | Sí |

## Integrantes del Grupo 1

- **David Usiña**
- **Mariuxi León**
- **Darwin Bonilla**
- **Patricio Jarrín**
