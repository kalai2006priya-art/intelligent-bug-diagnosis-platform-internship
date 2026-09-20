import pytest

def test_signup_successful(client):
    payload = {
        "name": "Alice Developer",
        "email": "alice@company.org",
        "password": "securepassword123"
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@company.org"
    assert data["user"]["name"] == "Alice Developer"

def test_signup_duplicate_email(client):
    payload = {
        "name": "Alice Duplicate",
        "email": "alice@company.org",
        "password": "anotherpassword"
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_login_successful(client):
    payload = {
        "email": "alice@company.org",
        "password": "securepassword123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    payload = {
        "email": "alice@company.org",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401

def test_protected_route_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_protected_route_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dev_tester@example.com"
