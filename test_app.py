import httpx
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app, Product, User

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_health_check(session):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}


def test_route_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_create_product(session):
    product_data = {"name": "Laptop", "price": 999.99, "stock": 10}

    response = client.post("/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["id"] is not None


def test_get_product_not_found(session):
    response = client.get("/products/9999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()


def test_delete_product(session):
    product = Product(name="Phone", price=599, stock=5)
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.delete(f"/products/{product.id}")
    assert response.status_code == 204

    response = client.get(f"/products/{product.id}")
    assert response.status_code == 404


def test_file_upload():
    test_file_content = b"test image content"
    files = {"file": ("test.jpg", test_file_content, "image/jpeg")}

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.jpg"
    assert data["size"] == len(test_file_content)


def test_file_upload_invalid_type():
    files = {"file": ("test.txt", b"not an image", "text/plain")}

    response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert "not allowed" in response.text


def test_weather_endpoint():
    mock_response = {
        "main": {"temp": 25},
        "weather": [{"description": "clear sky"}],
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(
            200,
            json=mock_response,
            request=httpx.Request("GET", "https://example.com"),
        )

        response = client.get("/weather/Nairobi")

        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == 25
        assert data["conditions"] == "clear sky"


def test_weather_endpoint_timeout():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        response = client.get("/weather/Nairobi")

        assert response.status_code == 503
        assert "timed out" in response.text


# ---- Exercise 1: User CRUD tests ----


def test_create_user_success(session):
    response = client.post(
        "/users", json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["id"] is not None


def test_create_user_duplicate_email(session):
    client.post("/users", json={"name": "Alice", "email": "alice@example.com"})

    response = client.post(
        "/users", json={"name": "Alice Clone", "email": "alice@example.com"}
    )

    assert response.status_code == 400
    assert "already registered" in response.text.lower()


def test_create_user_invalid_data(session):
    response = client.post("/users", json={"name": "Bob"})  # missing email
    assert response.status_code == 422


def test_get_user_success(session):
    create_response = client.post(
        "/users", json={"name": "Carol", "email": "carol@example.com"}
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Carol"


def test_get_user_not_found(session):
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()


def test_update_user_success(session):
    create_response = client.post(
        "/users", json={"name": "Dana", "email": "dana@example.com"}
    )
    user_id = create_response.json()["id"]

    response = client.put(f"/users/{user_id}", json={"name": "Dana Updated"})

    assert response.status_code == 200
    assert response.json()["name"] == "Dana Updated"


def test_update_user_invalid_data(session):
    create_response = client.post(
        "/users", json={"name": "Eve", "email": "eve@example.com"}
    )
    user_id = create_response.json()["id"]

    response = client.put(f"/users/{user_id}", json={"name": 12345})

    assert response.status_code == 422


def test_delete_user_success(session):
    create_response = client.post(
        "/users", json={"name": "Frank", "email": "frank@example.com"}
    )
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


def test_delete_user_not_found(session):
    response = client.delete("/users/9999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()