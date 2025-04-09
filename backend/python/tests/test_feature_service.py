import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..models import Feature, Tag, FeatureValue
from ..services.feature_service import FeatureService
from ..schemas import FeatureCreate, FeatureUpdate, FeatureValueCreate

@pytest.fixture
def feature_service(db_session: Session):
    return FeatureService(db_session)

@pytest.fixture
def sample_feature_data() -> Dict[str, Any]:
    return {
        "name": "test_feature",
        "description": "Test feature for unit tests",
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
def sample_feature_value_data() -> Dict[str, Any]:
    return {
        "entity_id": 1,
        "value": 50
    }

async def test_create_feature(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test feature creation"""
    feature_create = FeatureCreate(**sample_feature_data)
    feature = await feature_service.create_feature(feature_create)
    
    assert feature.name == sample_feature_data["name"]
    assert feature.description == sample_feature_data["description"]
    assert feature.data_type == sample_feature_data["data_type"]
    assert feature.constraints == sample_feature_data["constraints"]
    assert feature.is_active == sample_feature_data["is_active"]
    assert feature.importance_score == sample_feature_data["importance_score"]
    assert feature.category == sample_feature_data["category"]
    assert len(feature.tags) == len(sample_feature_data["tags"])
    assert all(tag.name in sample_feature_data["tags"] for tag in feature.tags)

async def test_get_feature(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test getting a feature by ID"""
    # First create a feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Then retrieve it
    feature = await feature_service.get_feature(created_feature.id)
    assert feature is not None
    assert feature.id == created_feature.id
    assert feature.name == sample_feature_data["name"]

async def test_get_features(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test getting features with filters"""
    # Create multiple features
    feature_create = FeatureCreate(**sample_feature_data)
    await feature_service.create_feature(feature_create)
    
    sample_feature_data["name"] = "test_feature2"
    feature_create2 = FeatureCreate(**sample_feature_data)
    await feature_service.create_feature(feature_create2)
    
    # Test different filter combinations
    features = await feature_service.get_features(
        skip=0,
        limit=10,
        search="test",
        category="test_category",
        is_active=True,
        tags=["test_tag1"]
    )
    
    assert len(features) == 2
    assert all(feature.category == "test_category" for feature in features)
    assert all(feature.is_active for feature in features)

async def test_update_feature(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test updating a feature"""
    # First create a feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Update the feature
    update_data = {
        "name": "updated_feature",
        "description": "Updated description",
        "tags": ["new_tag"]
    }
    feature_update = FeatureUpdate(**update_data)
    updated_feature = await feature_service.update_feature(created_feature.id, feature_update)
    
    assert updated_feature.name == update_data["name"]
    assert updated_feature.description == update_data["description"]
    assert len(updated_feature.tags) == 1
    assert updated_feature.tags[0].name == "new_tag"

async def test_delete_feature(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test deleting a feature"""
    # First create a feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Delete the feature
    result = await feature_service.delete_feature(created_feature.id)
    assert result is True
    
    # Try to get the deleted feature
    feature = await feature_service.get_feature(created_feature.id)
    assert feature is None

async def test_validate_feature_value(feature_service: FeatureService, sample_feature_data: Dict[str, Any]):
    """Test feature value validation"""
    # Create a feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Test valid value
    validation = await feature_service.validate_feature_value(created_feature.id, 50)
    assert validation.is_valid is True
    assert len(validation.errors) == 0
    
    # Test invalid value (out of range)
    validation = await feature_service.validate_feature_value(created_feature.id, 150)
    assert validation.is_valid is False
    assert len(validation.errors) > 0
    
    # Test invalid value (wrong type)
    validation = await feature_service.validate_feature_value(created_feature.id, "not a number")
    assert validation.is_valid is False
    assert len(validation.errors) > 0

async def test_set_feature_value(feature_service: FeatureService, sample_feature_data: Dict[str, Any], sample_feature_value_data: Dict[str, Any]):
    """Test setting feature values"""
    # Create a feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Set a value
    value_create = FeatureValueCreate(**sample_feature_value_data)
    feature_value = await feature_service.set_feature_value(created_feature.id, value_create)
    
    assert feature_value.feature_id == created_feature.id
    assert feature_value.entity_id == sample_feature_value_data["entity_id"]
    assert feature_value.value == sample_feature_value_data["value"]

async def test_get_feature_values(feature_service: FeatureService, sample_feature_data: Dict[str, Any], sample_feature_value_data: Dict[str, Any]):
    """Test getting feature values"""
    # Create a feature and set some values
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    value_create = FeatureValueCreate(**sample_feature_value_data)
    await feature_service.set_feature_value(created_feature.id, value_create)
    
    # Get values
    values = await feature_service.get_feature_values(
        created_feature.id,
        entity_ids=[sample_feature_value_data["entity_id"]],
        skip=0,
        limit=10
    )
    
    assert len(values) == 1
    assert values[0].feature_id == created_feature.id
    assert values[0].entity_id == sample_feature_value_data["entity_id"]
    assert values[0].value == sample_feature_value_data["value"]

@pytest.mark.parametrize("data_type,value,expected_valid", [
    ("numeric", 50, True),
    ("numeric", "not a number", False),
    ("numeric", -10, False),  # Below min
    ("numeric", 150, False),  # Above max
    ("categorical", "category1", True),
    ("categorical", "invalid_category", False),
    ("boolean", True, True),
    ("boolean", "not a boolean", False),
    ("text", "valid text", True),
    ("text", "x" * 1000, False),  # Exceeds max_length
    ("date", "2024-03-20T12:00:00Z", True),
    ("date", "invalid date", False),
])
async def test_feature_value_validation_cases(
    feature_service: FeatureService,
    sample_feature_data: Dict[str, Any],
    data_type: str,
    value: Any,
    expected_valid: bool
):
    """Test various feature value validation cases"""
    # Modify sample data for each test case
    sample_feature_data["data_type"] = data_type
    if data_type == "categorical":
        sample_feature_data["constraints"] = {"categories": ["category1", "category2"]}
    elif data_type == "text":
        sample_feature_data["constraints"] = {"max_length": 100}
    
    # Create feature
    feature_create = FeatureCreate(**sample_feature_data)
    created_feature = await feature_service.create_feature(feature_create)
    
    # Validate value
    validation = await feature_service.validate_feature_value(created_feature.id, value)
    assert validation.is_valid == expected_valid 