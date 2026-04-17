import pytest


def test_register_happy_path(client):
    response = client.post("/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
    })
    assert response.status_code == 200


def test_register_returns_success_message(client):
    response = client.post("/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
    })
    assert response.json() == {"message": "User registered"}


def test_register_does_not_contain_password(client):
    response = client.post("/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "strongpass",
    })
    assert "strongpass" not in response.text


@pytest.mark.parametrize("case,payload", [
    ("missing_email",        {"username": "u", "password": "p"}),
    ("missing_username",     {"email": "a@b.com", "password": "p"}),
    ("missing_password",     {"email": "a@b.com", "username": "u"}),
    ("empty_body",           {}),
    ("email_as_int",         {"email": 12345, "username": "u", "password": "p"}),
    ("invalid_email_format", {"email": "not-an-email", "username": "u", "password": "p"}),
    ("email_no_atsign",      {"email": "nosign.com", "username": "u", "password": "p"}),
])
def test_register_invalid_input_returns_422(client, case, payload):
    response = client.post("/register", json=payload)
    assert response.status_code == 422, f"case: {case}"


def test_register_duplicate_email_returns_400(client, sample_user):
    response = client.post("/register", json={
        "email": "sample@test.com",
        "username": "differentuser",
        "password": "strongpass",
    })
    assert response.status_code == 400


def test_register_duplicate_username_returns_400(client, sample_user):
    response = client.post("/register", json={
        "email": "different@test.com",
        "username": "sampleuser",
        "password": "strongpass",
    })
    assert response.status_code == 400
