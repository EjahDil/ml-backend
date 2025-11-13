import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlmodel import Session
from src.main import app 
from src.schemas.churn_input import ChurnInput

# Sample input payload for prediction
sample_payload = {
    "feature1": 1,
    "feature2": 0,
    "feature3": 5.4,
    # Add all required features expected by ChurnInput here
}

@pytest.fixture
def client():
    return TestClient(app)

# Mock for ModelArtifacts singleton model and feature engineering transform
def mock_model_predict(X):
    return [1]  # Predicted class

def mock_model_predict_proba(X):
    return [[0.3, 0.7]]  # Probability for class 1

def mock_transform(df):
    return df  # Assume transformation is identity for testing

# Test /predict/ endpoint using ModelArtifacts
@patch("app.routers.predict.ModelArtifacts.model", new_callable=MagicMock)
@patch("app.routers.predict.ModelArtifacts.fe", new_callable=MagicMock)
def test_predict_churn(mock_fe, mock_model, client):
    # Setup mocks
    mock_model.predict.side_effect = mock_model_predict
    mock_model.predict_proba.side_effect = mock_model_predict_proba
    mock_fe.transform.side_effect = mock_transform

    # Prepare payload matching ChurnInput schema
    payload = sample_payload

    # Provide fake user authentication dependency override if needed
    # client.app.dependency_overrides[get_current_user] = lambda: FakeUserObject()

    response = client.post("/predict/", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert data["prediction"] == 1
    assert abs(data["probability"] - 0.7) < 1e-5

# Test /predict/best_model using get_model_instance mock
@patch("app.routers.predict.get_model_instance")
def test_predict_best_model(mock_get_model_instance, client):
    # Mock model object with predict and predict_proba methods
    mock_model = MagicMock()
    mock_model.predict.return_value = [0]
    mock_model.predict_proba.return_value = [[0.8, 0.2]]
    mock_get_model_instance.return_value = mock_model

    payload = sample_payload

    response = client.post("/predict/best_model", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["prediction"] == 0
    assert abs(data["probability"] - 0.2) < 1e-5
    assert "model_version" in data

# Test /predict-from-call-session/ endpoint
@patch("app.routers.predict.ModelArtifacts.model", new_callable=MagicMock)
@patch("app.routers.predict.ModelArtifacts.fe", new_callable=MagicMock)
def test_predict_from_call_session(mock_fe, mock_model, client):
    mock_model.predict.side_effect = mock_model_predict
    mock_model.predict_proba.side_effect = mock_model_predict_proba
    mock_fe.transform.side_effect = mock_transform

    # Prepare request with customer_id and data
    payload = {
        "customer_id": "cust_12345",
        "data": sample_payload
    }

    response = client.post("/predict/predict-from-call-session/", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["external_customer_id"] == "cust_12345"
    assert data["prediction"] == 1
    assert abs(data["probability"] - 0.7) < 1e-5

# Add tests for GET /predictions/ and DELETE /predictions/{id} as needed with db setup or mocks.
