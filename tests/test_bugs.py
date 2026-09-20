import io
import pytest

def test_create_bug_successful(client, auth_headers):
    payload = {
        "title": "Login fails with NullPointerException",
        "description": "User clicks login button and receives internal 500 error instead of redirecting to dashboard.",
        "stack_trace": "java.lang.NullPointerException at AuthService.login(AuthService.java:45)",
        "component": "Authentication",
        "environment": "Production Linux Docker"
    }
    response = client.post("/bugs", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "Submitted"
    assert "id" in data

def test_create_bug_invalid_fields(client, auth_headers):
    # Missing required title and description
    response = client.post("/bugs", json={"title": "hi"}, headers=auth_headers)
    assert response.status_code == 422

def test_get_bug_by_id(client, auth_headers):
    # First create
    create_resp = client.post("/bugs", json={
        "title": "Database connection timeout during load",
        "description": "Connection pool exhausted after 50 concurrent requests."
    }, headers=auth_headers)
    bug_id = create_resp.json()["id"]

    # Now get
    get_resp = client.get(f"/bugs/{bug_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == bug_id

def test_list_bugs(client, auth_headers):
    response = client.get("/bugs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_upload_valid_log_file(client, auth_headers):
    log_content = (
        "2026-09-18 10:00:00 [ERROR] Connection failed\n"
        "java.lang.NullPointerException\n"
        "\tat com.example.service.AuthService.authenticate(AuthService.java:55)\n"
    )
    file_bytes = log_content.encode("utf-8")
    files = {"file": ("crash.log", io.BytesIO(file_bytes), "text/plain")}
    response = client.post("/bugs/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "stack_trace" in data
    assert "AuthService.java:55" in data["stack_trace"]
    assert data["detected_format"] == "LOG"

def test_upload_unsupported_file_extension(client, auth_headers):
    files = {"file": ("malicious.exe", io.BytesIO(b"binarycontent"), "application/octet-stream")}
    response = client.post("/bugs/upload", files=files, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]

def test_upload_empty_file(client, auth_headers):
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    response = client.post("/bugs/upload", files=files, headers=auth_headers)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
