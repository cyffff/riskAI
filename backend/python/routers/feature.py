from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.feature_service import FeatureService
from ..schemas import (
    Feature, FeatureCreate, FeatureUpdate,
    FeatureValue, FeatureValueCreate, FeatureValueUpdate,
    FeatureValidation
)

router = APIRouter(prefix="/api/v1/features", tags=["features"])

@router.post("", response_model=Feature)
async def create_feature(
    feature: FeatureCreate,
    db: Session = Depends(get_db)
):
    """Create a new feature."""
    service = FeatureService(db)
    return await service.create_feature(feature)

@router.get("", response_model=List[Feature])
async def get_features(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """Get features with filtering and pagination."""
    service = FeatureService(db)
    return await service.get_features(
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        is_active=is_active,
        tags=tags
    )

@router.get("/{feature_id}", response_model=Feature)
async def get_feature(
    feature_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific feature by ID."""
    service = FeatureService(db)
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.put("/{feature_id}", response_model=Feature)
async def update_feature(
    feature_id: int,
    feature: FeatureUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific feature."""
    service = FeatureService(db)
    updated_feature = await service.update_feature(feature_id, feature)
    if not updated_feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return updated_feature

@router.delete("/{feature_id}")
async def delete_feature(
    feature_id: int,
    db: Session = Depends(get_db)
):
    """Delete (soft delete) a feature."""
    service = FeatureService(db)
    if not await service.delete_feature(feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"message": "Feature deleted successfully"}

@router.post("/{feature_id}/values", response_model=FeatureValue)
async def set_feature_value(
    feature_id: int,
    value: FeatureValueCreate,
    db: Session = Depends(get_db)
):
    """Set a value for a feature."""
    service = FeatureService(db)
    return await service.set_feature_value(feature_id, value)

@router.get("/{feature_id}/values", response_model=List[FeatureValue])
async def get_feature_values(
    feature_id: int,
    entity_ids: Optional[List[int]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get values for a feature."""
    service = FeatureService(db)
    return await service.get_feature_values(
        feature_id,
        entity_ids=entity_ids,
        skip=skip,
        limit=limit
    )

@router.post("/{feature_id}/validate", response_model=FeatureValidation)
async def validate_feature_value(
    feature_id: int,
    value: any,
    db: Session = Depends(get_db)
):
    """Validate a value for a feature."""
    service = FeatureService(db)
    return await service.validate_feature_value(feature_id, value) 