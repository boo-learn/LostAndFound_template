import pytest


@pytest.mark.asyncio
async def test_users_crud_happy_path(client):
    # Create
    payload = {
        "username": "user1",
        "password": "pass12345",
        "email": "user1@example.com",
        "full_name": "User One",
    }
    r = await client.post("/users/", json=payload)
    assert r.status_code in (200, 201)
    created = r.json()
    assert created["username"] == payload["username"]
    user_id = created["id"]

    # List
    r = await client.get("/users/")
    assert r.status_code == 200
    users = r.json()
    assert any(u["id"] == user_id for u in users)

    # Get by id
    r = await client.get(f"/users/{user_id}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["username"] == payload["username"]

    # Update profile fields (email/full_name)
    upd = {"email": "new1@example.com", "full_name": "User One Updated"}
    r = await client.put(f"/users/{user_id}", json=upd)
    assert r.status_code == 200
    updated = r.json()
    assert updated["email"] == "new1@example.com"
    assert updated["full_name"] == "User One Updated"

    # Update password and verify login works with new password
    upd_pass = {"password": "newPass987"}
    r = await client.put(f"/users/{user_id}", json=upd_pass)
    assert r.status_code == 200

    # login with new password
    r = await client.post(
        "/token",
        data={"username": payload["username"], "password": "newPass987"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # Delete
    r = await client.delete(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.json() == {"success": True}

    # Ensure deleted
    r = await client.get(f"/users/{user_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_users_duplicate_username_returns_400(client):
    payload = {"username": "dup", "password": "x1234567"}
    r1 = await client.post("/users/", json=payload)
    assert r1.status_code in (200, 201)
    r2 = await client.post("/users/", json=payload)
    assert r2.status_code == 400


@pytest.mark.asyncio
async def test_users_not_found_cases(client):
    # get 404
    r = await client.get("/users/99999")
    assert r.status_code == 404

    # delete 404
    r = await client.delete("/users/99999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_users_create_validation_errors(client):
    # missing username
    r = await client.post("/users/", json={"password": "abc12345"})
    assert r.status_code == 422

    # missing password
    r = await client.post("/users/", json={"username": "nouser"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_users_response_does_not_expose_password(client):
    payload = {"username": "safeuser", "password": "abc12345"}
    r = await client.post("/users/", json=payload)
    assert r.status_code in (200, 201)
    data = r.json()
    assert "password" not in data
    assert "hashed_password" not in data

    user_id = data["id"]
    r = await client.get(f"/users/{user_id}")
    assert r.status_code == 200
    data = r.json()
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_users_update_empty_body_ok(client):
    payload = {"username": "emptyupd", "password": "startpass1"}
    r = await client.post("/users/", json=payload)
    assert r.status_code in (200, 201)
    user_id = r.json()["id"]

    # пустое обновление — должно вернуть 200 и не менять критичных полей
    r = await client.put(f"/users/{user_id}", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "emptyupd"


@pytest.mark.asyncio
async def test_users_update_not_found_404(client):
    r = await client.put("/users/123456", json={"full_name": "X"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_users_deactivate_and_login_fail(client):
    # create
    payload = {"username": "inactive", "password": "passInactive1"}
    r = await client.post("/users/", json=payload)
    assert r.status_code in (200, 201)
    user_id = r.json()["id"]

    # deactivate
    r = await client.put(f"/users/{user_id}", json={"is_active": False})
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # login should fail
    r = await client.post(
        "/token",
        data={"username": payload["username"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401

