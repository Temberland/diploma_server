def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "user@test.com",
        "password": "password123",
        "currency": "R"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    response = client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    assert response.status_code == 400
    assert "уже зарегистрирован" in response.json()["detail"]


def test_register_short_password(client):
    response = client.post("/auth/register", json={
        "email": "user@test.com",
        "password": "123"
    })
    assert response.status_code == 422  # Pydantic валидация


def test_login_success(client):
    client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    response = client.post("/auth/login", json={"email": "user@test.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    response = client.post("/auth/login", json={"email": "user@test.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={"email": "nobody@test.com", "password": "password123"})
    assert response.status_code == 401


def test_refresh_token(client):
    reg = client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    refresh_token = reg.json()["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_reuse(client):
    """Нельзя использовать refresh токен дважды"""
    reg = client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    refresh_token = reg.json()["refresh_token"]
    client.post("/auth/refresh", json={"refresh_token": refresh_token})
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


def test_logout(client):
    reg = client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    token = reg.json()["access_token"]
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_me_authorized(auth_client):
    response = auth_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"


def test_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
