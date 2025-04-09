from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..schemas import (
    Feature, FeatureCreate, FeatureUpdate,
    RiskFactor, RiskFactorCreate, RiskFactorUpdate,
    RiskAssessmentRequest, RiskAssessmentResponse,
    PaginatedResponse
)
from ..services.risk_assessment import RiskAssessmentService
from ..services.feature_management import FeatureManagementService

router = APIRouter(prefix="/api/v1", tags=["risk-assessment"])

# Feature Management Endpoints
@router.post("/features", response_model=Feature)
async def create_feature(
    feature: FeatureCreate,
    db: Session = Depends(get_db)
):
    """Create a new feature for risk assessment."""
    service = FeatureManagementService(db)
    return await service.create_feature(feature)

@router.get("/features", response_model=PaginatedResponse)
async def list_features(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List features with pagination and optional filtering."""
    service = FeatureManagementService(db)
    return await service.list_features(page, page_size, is_active)

@router.get("/features/{feature_id}", response_model=Feature)
async def get_feature(
    feature_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific feature by ID."""
    service = FeatureManagementService(db)
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.put("/features/{feature_id}", response_model=Feature)
async def update_feature(
    feature_id: int,
    feature: FeatureUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific feature."""
    service = FeatureManagementService(db)
    updated_feature = await service.update_feature(feature_id, feature)
    if not updated_feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return updated_feature

# Risk Factor Endpoints
@router.post("/risk-factors", response_model=RiskFactor)
async def create_risk_factor(
    risk_factor: RiskFactorCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk factor."""
    service = RiskAssessmentService(db)
    return await service.create_risk_factor(risk_factor)

@router.get("/risk-factors", response_model=PaginatedResponse)
async def list_risk_factors(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    feature_id: int = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List risk factors with pagination and optional filtering."""
    service = RiskAssessmentService(db)
    return await service.list_risk_factors(page, page_size, feature_id, is_active)

@router.put("/risk-factors/{risk_factor_id}", response_model=RiskFactor)
async def update_risk_factor(
    risk_factor_id: int,
    risk_factor: RiskFactorUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific risk factor."""
    service = RiskAssessmentService(db)
    updated_factor = await service.update_risk_factor(risk_factor_id, risk_factor)
    if not updated_factor:
        raise HTTPException(status_code=404, detail="Risk factor not found")
    return updated_factor

# Risk Assessment Endpoints
@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    assessment: RiskAssessmentRequest,
    db: Session = Depends(get_db)
):
    """Perform a risk assessment based on provided features."""
    service = RiskAssessmentService(db)
    return await service.assess_risk(assessment)

@router.get("/assessments/{customer_id}", response_model=List[RiskAssessmentResponse])
async def get_customer_assessments(
    customer_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get risk assessment history for a specific customer."""
    service = RiskAssessmentService(db)
    return await service.get_customer_assessments(customer_id, start_date, end_date)

@router.get("/assessments/stats", response_model=dict)
async def get_assessment_stats(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get statistical summary of risk assessments."""
    service = RiskAssessmentService(db)
    return await service.get_assessment_stats(start_date, end_date) 