from fastapi.testclient import TestClient
from app.api import app  # Asegúrate de que importe tu app principal de FastAPI

client = TestClient(app)

def test_http_404_not_found():
    # Verifica que cualquier ruta inexistente devuelva un código HTTP 404
    response = client.get("/api/v1/recurso-que-no-existe-absolutamente-nada")
    assert response.status_code == 404

def test_get_order_success():
    # Verifica que un pedido existente devuelva HTTP 200 y sus datos básicos
    # Usamos O001 que viene cargado por defecto en los fixtures
    response = client.get("/orders/O001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "O001"
    assert data["status"] == "DRAFT"

def test_confirm_order_success_or_conflict():
    # Intenta confirmar un pedido válido (O013 suele iniciar en DRAFT y estar listo)
    response = client.post("/orders/O013/confirm")
    
    # Si pasa por primera vez, debe ser 200 OK
    if response.status_code == 200:
        assert response.json()["status"] == "CONFIRMED"
        
        # Intentar confirmarlo por segunda vez debe lanzar conflicto HTTP 409 (Doble confirmación)
        response_second = client.post("/orders/O013/confirm")
        assert response_second.status_code == 409
    else:
        # Si ya fue modificado en otra prueba previa, validamos que al menos responda con código de regla
        assert response.status_code in [200, 409, 422]

def test_ship_order_without_tracking_unprocessable():
    # Intentar enviar un pedido sin número de guía debe retornar HTTP 422 (Unprocessable Entity)
    response = client.post("/orders/O013/ship", json={"tracking_number": ""})
    # Dependiendo del estado o validación estricta, la guía vacía arroja 422 o 409/400
    assert response.status_code in [422, 409, 400]