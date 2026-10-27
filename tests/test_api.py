from fastapi.testclient import TestClient
from app.api import app  # Asegúrate de que importe tu app principal de FastAPI

client = TestClient(app)

def test_http_404_not_found():
    # Verifica que cualquier ruta inexistente devuelva un código HTTP 404
    response = client.get("/api/v1/recurso-que-no-existe-absolutamente-nada")
    assert response.status_code == 404