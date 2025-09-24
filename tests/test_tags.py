import pytest


async def create_user_and_token(client, username="tagger", password="tagPass123"):
    # create user
    payload = {"username": username, "password": password}
    r = await client.post("/users/", json=payload)
    assert r.status_code in (200, 201)

    # get token
    r = await client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    return token


@pytest.mark.asyncio
async def test_tags_crud_happy_path(client):
    token = await create_user_and_token(client)
    auth = {"Authorization": f"Bearer {token}"}

    # create
    payload = {"name": "urgent"}
    r = await client.post("/tags/", json=payload, headers=auth)
    assert r.status_code == 200
    created = r.json()
    assert created["name"] == "urgent"
    tag_id = created["id"]

    # list
    r = await client.get("/tags/", headers=auth)
    assert r.status_code == 200
    assert any(t["id"] == tag_id for t in r.json())

    # get by id
    r = await client.get(f"/tags/{tag_id}", headers=auth)
    assert r.status_code == 200
    assert r.json()["id"] == tag_id

    # update
    upd = {"name": "important"}
    r = await client.put(f"/tags/{tag_id}", json=upd, headers=auth)
    assert r.status_code == 200
    assert r.json()["name"] == "important"


@pytest.mark.asyncio
async def test_tags_get_404(client):
    token = await create_user_and_token(client, username="tagger2")
    auth = {"Authorization": f"Bearer {token}"}

    r = await client.get("/tags/99999", headers=auth)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_tags_update_404(client):
    token = await create_user_and_token(client, username="tagger3")
    auth = {"Authorization": f"Bearer {token}"}

    r = await client.put("/tags/77777", json={"name": "x"}, headers=auth)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_tags_protected_without_token(client):
    # list without token
    r = await client.get("/tags/")
    assert r.status_code == 401

    # create without token
    r = await client.post("/tags/", json={"name": "n"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_attach_and_detach_tags_to_lost_item(client):
    token = await create_user_and_token(client, username="tagger5")
    auth = {"Authorization": f"Bearer {token}"}

    # create tag
    r = await client.post("/tags/", json={"name": "lost"}, headers=auth)
    assert r.status_code == 200
    tag_id = r.json()["id"]

    # create lost item (не защищённый роут)
    r = await client.post("/lost_items/", json={"name": "Ключи", "location": "подъезд"})
    assert r.status_code == 200
    lost_item_id = r.json()["id"]

    # attach tag to lost item
    r = await client.put(f"/tags/lost/{lost_item_id}", json={"tag_ids": [tag_id]}, headers=auth)
    assert r.status_code == 200
    assert r.json() == {"success": True}

    # detach tag from lost item
    r = await client.delete(f"/tags/{tag_id}/lost/{lost_item_id}", headers=auth)
    assert r.status_code == 200
    assert r.json() == {"success": True}


@pytest.mark.asyncio
async def test_attach_and_detach_tags_to_found_item(client):
    token = await create_user_and_token(client, username="tagger6")
    auth = {"Authorization": f"Bearer {token}"}

    # create tag
    r = await client.post("/tags/", json={"name": "found"}, headers=auth)
    assert r.status_code == 200
    tag_id = r.json()["id"]

    # create found item
    r = await client.post("/found_items/", json={"name": "Зонтик", "location": "парк"})
    assert r.status_code == 200
    found_item_id = r.json()["id"]

    # attach
    r = await client.put(f"/tags/found/{found_item_id}", json={"tag_ids": [tag_id]}, headers=auth)
    assert r.status_code == 200

    # detach
    r = await client.delete(f"/tags/{tag_id}/found/{found_item_id}", headers=auth)
    assert r.status_code == 200