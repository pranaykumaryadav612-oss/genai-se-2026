# test_src/apis/activate_account.py

import pytest
from fastapi.testclient import TestClient
from src.apis.activate_account import router
from src.schemas.activate_account import ActivateAccountRequest, ActivateAccountResponse

client = TestClient(router)

def test_activate_account_happy_path():
    """
    Test the happy path: Activate a user account with valid credentials
    """
    request_body = {
        "user_id": 1,
        "activation_code": "123456"
    }
    response = client.post("/activate-account", json=request_body)
    assert response.status_code == 200
    assert response.json()["message"] == "Account activated successfully"

def test_activate_account_invalid_user_id():
    """
    Test edge case: Activate a user account with invalid user ID
    """
    request_body = {
        "user_id": "invalid",
        "activation_code": "123456"
    }
    response = client.post("/activate-account", json=request_body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "user_id"]
    assert response.json()["detail"][0]["msg"] == "value is not a valid integer"

def test_activate_account_invalid_activation_code():
    """
    Test edge case: Activate a user account with invalid activation code
    """
    request_body = {
        "user_id": 1,
        "activation_code": "invalid"
    }
    response = client.post("/activate-account", json=request_body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "activation_code"]
    assert response.json()["detail"][0]["msg"] == "value is not a valid string"

def test_activate_account_missing_user_id():
    """
    Test edge case: Activate a user account with missing user ID
    """
    request_body = {
        "activation_code": "123456"
    }
    response = client.post("/activate-account", json=request_body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "user_id"]
    assert response.json()["detail"][0]["msg"] == "field required"

def test_activate_account_missing_activation_code():
    """
    Test edge case: Activate a user account with missing activation code
    """
    request_body = {
        "user_id": 1
    }
    response = client.post("/activate-account", json=request_body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "activation_code"]
    assert response.json()["detail"][0]["msg"] == "field required"

def test_activate_account_internal_server_error():
    """
    Test negative case: Simulate an internal server error
    """
    # Simulate an internal server error by raising an exception
    with pytest.raises(Exception):
        client.post("/activate-account", json={"user_id": 1, "activation_code": "123456"})
    assert client.get("/activate-account").status_code == 500