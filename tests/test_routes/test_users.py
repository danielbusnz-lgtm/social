

def test_register_happy_path(client):
    response = client.post("/register", json = {
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
     })
    assert response.status_code == 200


def test_register_returns_200(client):
    response = client.post("/register", json = {
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
     })
    assert response.json() == {"message": "User registered"}


def test_register_not_containt_password(client):
    response = client.post("/register", json = {
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
     })
    assert "strongpass" not in response.txt


