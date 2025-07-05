import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("AUTH0_DOMAIN", "test.auth0.com")
    monkeypatch.setenv("AUTH0_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("AUTH0_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("AUTH0_AUDIENCE", "test_audience")

@patch('requests.post')
def test_login_user_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "fake_token", "token_type": "bearer"}
    mock_post.return_value = mock_response

    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 200
    assert response.json() == {"access_token": "fake_token", "token_type": "bearer"}

@patch('requests.post')
def test_login_user_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_grant"}
    mock_post.return_value = mock_response

    response = client.post("/auth/login", json={"email": "test@example.com", "password": "wrongpassword"})

    assert response.status_code == 400
    assert response.json() == {'detail': {'error': 'invalid_grant'}}

@patch('requests.post')
def test_register_user_success(mock_post):
    mock_token_response = MagicMock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {"access_token": "fake_mgmt_token"}

    mock_user_response = MagicMock()
    mock_user_response.status_code = 201
    mock_user_response.json.return_value = {"user_id": "auth0|12345"}

    mock_post.side_effect = [mock_token_response, mock_user_response]

    response = client.post("/auth/register", json={"email": "newuser@example.com", "password": "newpassword"})

    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully."}

@patch('requests.post')
def test_register_user_token_failure(mock_post):
    mock_token_response = MagicMock()
    mock_token_response.status_code = 400
    mock_token_response.json.return_value = {"error": "unauthorized_client"}
    mock_post.return_value = mock_token_response

    response = client.post("/auth/register", json={"email": "newuser@example.com", "password": "newpassword"})

    assert response.status_code == 400
    assert response.json() == {'detail': {'error': 'unauthorized_client'}}

@patch('requests.post')
def test_register_user_creation_failure(mock_post):
    mock_token_response = MagicMock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {"access_token": "fake_mgmt_token"}

    mock_user_response = MagicMock()
    mock_user_response.status_code = 409
    mock_user_response.json.return_value = {"error": "user_exists"}

    mock_post.side_effect = [mock_token_response, mock_user_response]

    response = client.post("/auth/register", json={"email": "existinguser@example.com", "password": "password"})

    assert response.status_code == 400
    assert response.json() == {'detail': {'error': 'user_exists'}}
