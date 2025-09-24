import pytest


@pytest.mark.asyncio
async def test_token_success_and_protected_access(client):
    # 1) создаём пользователя
    user_payload = {
        "username": "john",
        "password": "secret123",
        "email": "john@example.com",
        "full_name": "John Doe",
    }
    resp_create = await client.post("/users/", json=user_payload)
    assert resp_create.status_code in (200, 201)
    created = resp_create.json()
    assert created["username"] == user_payload["username"]

    # 2) получаем токен
    resp_token = await client.post(
        "/token",
        data={"username": user_payload["username"], "password": user_payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_token.status_code == 200
    token_data = resp_token.json()
    assert "access_token" in token_data
    assert token_data.get("token_type") == "bearer"

    # 3) доступ к защищённому эндпоинту с токеном
    resp_protected = await client.get(
        "/tags/", headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert resp_protected.status_code == 200
    assert isinstance(resp_protected.json(), list)


@pytest.mark.asyncio
async def test_token_invalid_credentials(client):
    # создаём пользователя
    user_payload = {
        "username": "alice",
        "password": "correctPass1",
        "email": "alice@example.com",
        "full_name": "Alice",
    }
    resp_create = await client.post("/users/", json=user_payload)
    assert resp_create.status_code in (200, 201)

    # пробуем получить токен с неверным паролем
    resp_token_bad = await client.post(
        "/token",
        data={"username": user_payload["username"], "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_token_bad.status_code == 401


@pytest.mark.asyncio
async def test_protected_without_token_unauthorized(client):
    # доступ к защищённому эндпоинту без токена должен вернуть 401
    resp = await client.get("/tags/")
    assert resp.status_code == 401

