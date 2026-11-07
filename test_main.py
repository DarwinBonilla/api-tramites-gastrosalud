"""
test_main.py - Pruebas automatizadas con pytest (Centro Médico GastroSalud).

Ejecutar:   pytest -v
GitHub Actions las ejecuta automáticamente en cada push o pull_request.
"""

from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)


def obtener_token(usuario="ana", password="ana123"):
    respuesta = cliente.post(
        "/api/v1/token", data={"username": usuario, "password": password}
    )
    return respuesta.json()["access_token"]


def encabezado(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------- Pruebas mínimas exigidas por el taller ------------------
def test_sin_token_es_rechazado():
    respuesta = cliente.get("/api/v1/tramites")
    assert respuesta.status_code == 401


def test_con_token_valido_es_aceptado():
    respuesta = cliente.get(
        "/api/v1/tramites", headers=encabezado(obtener_token())
    )
    assert respuesta.status_code == 200
    assert len(respuesta.json()) >= 1


def test_tramite_inexistente_devuelve_404():
    respuesta = cliente.get(
        "/api/v1/tramites/9999", headers=encabezado(obtener_token())
    )
    assert respuesta.status_code == 404


# ------------------------ Pruebas adicionales -----------------------------
def test_password_incorrecta_devuelve_401():
    respuesta = cliente.post(
        "/api/v1/token", data={"username": "ana", "password": "equivocada"}
    )
    assert respuesta.status_code == 401


def test_token_alterado_es_rechazado():
    token = obtener_token() + "x"
    respuesta = cliente.get("/api/v1/tramites", headers=encabezado(token))
    assert respuesta.status_code == 401


def test_no_puede_ver_tramite_de_otro_usuario():
    # El trámite 3 pertenece a "luis"; "ana" no debe verlo (prevención BOLA/IDOR).
    respuesta = cliente.get("/api/v1/tramites/3", headers=encabezado(obtener_token()))
    assert respuesta.status_code == 404


def test_registrar_tramite_devuelve_201():
    respuesta = cliente.post(
        "/api/v1/tramites",
        json={"tipo": "Solicitud de duplicado de informe de Colonoscopia"},
        headers=encabezado(obtener_token()),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "Recibido"


def test_datos_clinicos_sensibles_no_se_exponen():
    # Verifica el cumplimiento de LOPDP y Acuerdo Ministerial 5216 (MSP):
    # Ni el diagnóstico CIE-10, ni el ID de historia clínica interna ni la factura PHP
    # deben filtrarse en la respuesta JSON de la API.
    respuesta = cliente.get("/api/v1/tramites/1", headers=encabezado(obtener_token()))
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert "propietario" not in cuerpo
    assert "cie10_confidencial" not in cuerpo
    assert "historia_clinica_interna" not in cuerpo
    assert "factura_php_id" not in cuerpo
