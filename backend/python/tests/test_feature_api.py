import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..main import app
from ..models import Feature, Tag
from ..schemas import FeatureCreate, FeatureUpdate

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_feature_data():
    return {
        "name": "test_feature",
        "description": "Test feature for API tests",
        "data_type": "numeric",
        "constraints": {
            "min": 0,
            "max": 100
        },
        "is_active": True,
        "importance_score": 0.8,
        "category": "test_category",
        "tags": ["test_tag1", "test_tag2"]
    }

@pytest.fixture
def sample_feature_value_data():
    return {
        "entity_id": 1,
        "value": 50
    }

def test_create_feature(client, sample_feature_data):
    """Test feature creation endpoint"""
    response = client.post("/api/v1/features", json=sample_feature_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == sample_feature_data["name"]
    assert data["description"] == sample_feature_data["description"]
    assert data["data_type"] == sample_feature_data["data_type"]
    assert data["constraints"] == sample_feature_data["constraints"]
    assert data["is_active"] == sample_feature_data["is_active"]
    assert data["importance_score"] == sample_feature_data["importance_score"]
    assert data["category"] == sample_feature_data["category"]
    assert len(data["tags"]) == len(sample_feature_data["tags"])

def test_get_features(client, sample_feature_data):
    """Test get features endpoint with filters"""
    # First create a feature
    client.post("/api/v1/features", json=sample_feature_data)
    
    # Test different query parameters
    response = client.get(
        "/api/v1/features",
        params={
            "skip": 0,
            "limit": 10,
            "search": "test",
            "category": "test_category",
            "is_active": True,
            "tags": ["test_tag1"]
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert all(feature["category"] == "test_category" for feature in data)
    assert all(feature["is_active"] for feature in data)

def test_get_feature(client, sample_feature_data):
    """Test get single feature endpoint"""
    # First create a feature
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    # Get the feature
    response = client.get(f"/api/v1/features/{feature_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == feature_id
    assert data["name"] == sample_feature_data["name"]

def test_update_feature(client, sample_feature_data):
    """Test feature update endpoint"""
    # First create a feature
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    # Update the feature
    update_data = {
        "name": "updated_feature",
        "description": "Updated description",
        "tags": ["new_tag"]
    }
    response = client.put(f"/api/v1/features/{feature_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert len(data["tags"]) == 1
    assert data["tags"][0] == "new_tag"

def test_delete_feature(client, sample_feature_data):
    """Test feature deletion endpoint"""
    # First create a feature
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    # Delete the feature
    response = client.delete(f"/api/v1/features/{feature_id}")
    assert response.status_code == 200
    
    # Try to get the deleted feature
    response = client.get(f"/api/v1/features/{feature_id}")
    assert response.status_code == 404

def test_set_feature_value(client, sample_feature_data, sample_feature_value_data):
    """Test setting feature value endpoint"""
    # First create a feature
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    # Set a value
    response = client.post(
        f"/api/v1/features/{feature_id}/values",
        json=sample_feature_value_data
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["feature_id"] == feature_id
    assert data["entity_id"] == sample_feature_value_data["entity_id"]
    assert data["value"] == sample_feature_value_data["value"]

def test_get_feature_values(client, sample_feature_data, sample_feature_value_data):
    """Test getting feature values endpoint"""
    # First create a feature and set a value
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    client.post(
        f"/api/v1/features/{feature_id}/values",
        json=sample_feature_value_data
    )
    
    # Get values
    response = client.get(
        f"/api/v1/features/{feature_id}/values",
        params={
            "entity_ids": [sample_feature_value_data["entity_id"]],
            "skip": 0,
            "limit": 10
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["feature_id"] == feature_id
    assert data[0]["entity_id"] == sample_feature_value_data["entity_id"]
    assert data[0]["value"] == sample_feature_value_data["value"]

def test_validate_feature_value(client, sample_feature_data):
    """Test feature value validation endpoint"""
    # First create a feature
    create_response = client.post("/api/v1/features", json=sample_feature_data)
    feature_id = create_response.json()["id"]
    
    # Test valid value
    response = client.post(
        f"/api/v1/features/{feature_id}/validate",
        json=50
    )
    assert response.status_code == 200
    assert response.json()["is_valid"] is True
    
    # Test invalid value
    response = client.post(
        f"/api/v1/features/{feature_id}/validate",
        json="not a number"
    )
    assert response.status_code == 200
    assert response.json()["is_valid"] is False

@pytest.mark.parametrize("invalid_data,expected_status", [
    ({"name": ""}, 422),  # Empty name
    ({"data_type": "invalid"}, 422),  # Invalid data type
    ({"importance_score": 2.0}, 422),  # Score out of range
    ({"constraints": {"min": 100, "max": 0}}, 422),  # Invalid constraints
])
def test_feature_validation_errors(client, sample_feature_data, invalid_data, expected_status):
    """Test validation errors in feature creation"""
    data = sample_feature_data.copy()
    data.update(invalid_data)
    
    response = client.post("/api/v1/features", json=data)
    assert response.status_code == expected_status

def test_feature_unique_name_constraint(client, sample_feature_data):
    """Test unique name constraint"""
    # Create first feature
    response = client.post("/api/v1/features", json=sample_feature_data)
    assert response.status_code == 200
    
    # Try to create another feature with the same name
    response = client.post("/api/v1/features", json=sample_feature_data)
    assert response.status_code == 400  # or your chosen error code for duplicates 