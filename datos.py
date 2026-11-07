"""
datos.py - Simulación del SISTEMA HEREDADO (Centro Médico GastroSalud Cía. Ltda.).

En la arquitectura AS-IS del Centro Médico de Especialidades Gastroenterológicas
del Ecuador (GastroSalud, Quito), los registros de trámites asistenciales,
órdenes de procedimientos (EDA y Colonoscopias), entrega de informes firmados y
conciliación con facturación PHP residen en un servidor físico Linux/MySQL local
sin exposición estandarizada hacia el Portal del Paciente ni la App Móvil.

Este módulo actúa como Capa Anticorrupción (ACL) sobre el sistema heredado,
conteniendo tanto atributos públicos del trámite como datos clínicos sensibles
(CIE-10, identificador interno de historia clínica y monto de facturación PHP)
que la API filtra antes de responder para cumplir con la LOPDP (2021) y el
Acuerdo Ministerial 5216 del MSP (2014).
"""

from datetime import date

# ---------------------------------------------------------------------------
# Usuarios autorizados a usar la API (Pacientes registrados en el Portal).
# La contraseña NUNCA se guarda en texto plano: se guarda su "hash" PBKDF2-SHA256.
# Usuarios de prueba:  ana / ana123   y   luis / luis123
# ---------------------------------------------------------------------------
USUARIOS = {
    "ana": {
        "usuario": "ana",
        "nombre": "Ana Torres (Paciente GastroSalud)",
        # hash PBKDF2-SHA256 de "ana123" (ver seguridad.py)
        "password_hash": "pbkdf2_sha256$100000$c2FsLWFuYQ==$qltsgcn6xIJpa7crMiL0BkrEHV92+WI3fDO2/hcGngM=",
    },
    "luis": {
        "usuario": "luis",
        "nombre": "Luis Mora (Paciente GastroSalud)",
        # hash PBKDF2-SHA256 de "luis123"
        "password_hash": "pbkdf2_sha256$100000$c2FsLWx1aXM=$Q604fA7gfLg4Z0zSp4yWtYOSQqVy4H5KbpYwc9fj+qQ=",
    },
}

# ---------------------------------------------------------------------------
# Trámites clínico-administrativos en el sistema heredado Linux/MySQL de GastroSalud.
# Nota de Seguridad (LOPDP / MSP 5216): Los campos 'propietario',
# 'historia_clinica_interna', 'cie10_confidencial' y 'factura_php_id' son datos
# internos/sensibles que permanecen en la base local y NO se exponen en el DTO público.
# ---------------------------------------------------------------------------
TRAMITES = {
    1: {
        "id": 1,
        "tipo": "Autorización de Endoscopia Digestiva Alta (EDA)",
        "especialidad": "Gastroenterología Clínica",
        "estado": "Aprobado",
        "fecha": date(2026, 10, 2),
        "propietario": "ana",
        "historia_clinica_interna": "HC-GS-2026-00142",
        "cie10_confidencial": "K29.7 - Gastritis, no especificada",
        "factura_php_id": "FAC-PHP-8821",
    },
    2: {
        "id": 2,
        "tipo": "Entrega de Informe Firmado y Capturas de Colonoscopia",
        "especialidad": "Endoscopia Digestiva",
        "estado": "En revisión",
        "fecha": date(2026, 10, 15),
        "propietario": "ana",
        "historia_clinica_interna": "HC-GS-2026-00142",
        "cie10_confidencial": "K63.5 - Pólipo del colon",
        "factura_php_id": "FAC-PHP-8904",
    },
    3: {
        "id": 3,
        "tipo": "Certificado Médico de Atención y Receta Firmada",
        "especialidad": "Gastroenterología Clínica",
        "estado": "Recibido",
        "fecha": date(2026, 10, 20),
        "propietario": "luis",
        "historia_clinica_interna": "HC-GS-2026-00319",
        "cie10_confidencial": "K21.0 - Enfermedad del reflujo gastroesofágico",
        "factura_php_id": "FAC-PHP-8950",
    },
}


def buscar_usuario(usuario: str):
    return USUARIOS.get(usuario)


def listar_tramites(propietario: str):
    return [t for t in TRAMITES.values() if t["propietario"] == propietario]


def buscar_tramite(tramite_id: int):
    return TRAMITES.get(tramite_id)


def registrar_tramite(tipo: str, propietario: str, especialidad: str = "Gastroenterología Clínica"):
    nuevo_id = max(TRAMITES) + 1 if TRAMITES else 1
    tramite = {
        "id": nuevo_id,
        "tipo": tipo,
        "especialidad": especialidad,
        "estado": "Recibido",
        "fecha": date.today(),
        "propietario": propietario,
        "historia_clinica_interna": f"HC-GS-2026-{nuevo_id:05d}",
        "cie10_confidencial": "RESERVADO-MSP-5216",
        "factura_php_id": f"PENDIENTE-PHP-{nuevo_id:04d}",
    }
    TRAMITES[nuevo_id] = tramite
    return tramite
