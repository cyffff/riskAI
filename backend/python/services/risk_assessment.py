from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..models import Feature, RiskFactor, RiskAssessment
from ..schemas import (
    RiskFactorCreate, RiskFactorUpdate,
    RiskAssessmentRequest, RiskAssessmentResponse
)

class RiskAssessmentService:
    def __init__(self, db: Session):
        self.db = db

    async def create_risk_factor(self, risk_factor: RiskFactorCreate) -> RiskFactor:
        """Create a new risk factor."""
        db_risk_factor = RiskFactor(**risk_factor.dict())
        self.db.add(db_risk_factor)
        await self.db.commit()
        await self.db.refresh(db_risk_factor)
        return db_risk_factor

    async def list_risk_factors(
        self,
        page: int,
        page_size: int,
        feature_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """List risk factors with pagination and filtering."""
        query = self.db.query(RiskFactor)
        
        if feature_id:
            query = query.filter(RiskFactor.feature_id == feature_id)
        if is_active is not None:
            query = query.filter(RiskFactor.is_active == is_active)

        total = await query.count()
        risk_factors = await query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "items": risk_factors,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_risk_factor(
        self,
        risk_factor_id: int,
        risk_factor: RiskFactorUpdate
    ) -> Optional[RiskFactor]:
        """Update a risk factor."""
        db_risk_factor = await self.db.query(RiskFactor).filter(
            RiskFactor.id == risk_factor_id
        ).first()

        if not db_risk_factor:
            return None

        for field, value in risk_factor.dict(exclude_unset=True).items():
            setattr(db_risk_factor, field, value)

        await self.db.commit()
        await self.db.refresh(db_risk_factor)
        return db_risk_factor

    async def assess_risk(self, assessment: RiskAssessmentRequest) -> RiskAssessmentResponse:
        """Perform risk assessment based on provided features."""
        # Get all active risk factors
        risk_factors = await self.db.query(RiskFactor).filter(
            RiskFactor.is_active == True
        ).all()

        # Calculate risk score based on risk factors
        total_score = 0
        max_possible_score = 0
        risk_details = []

        for factor in risk_factors:
            feature_value = assessment.features.get(factor.feature_id)
            if feature_value is not None:
                factor_score = self._calculate_factor_score(factor, feature_value)
                total_score += factor_score
                max_possible_score += factor.weight
                risk_details.append({
                    "factor_id": factor.id,
                    "score": factor_score,
                    "max_score": factor.weight
                })

        # Normalize score to 0-100 range
        normalized_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

        # Create risk assessment record
        db_assessment = RiskAssessment(
            customer_id=assessment.customer_id,
            risk_score=normalized_score,
            assessment_date=datetime.utcnow(),
            details=risk_details
        )
        self.db.add(db_assessment)
        await self.db.commit()
        await self.db.refresh(db_assessment)

        return RiskAssessmentResponse(
            id=db_assessment.id,
            customer_id=db_assessment.customer_id,
            risk_score=normalized_score,
            risk_level=self._determine_risk_level(normalized_score),
            assessment_date=db_assessment.assessment_date,
            details=risk_details
        )

    async def get_customer_assessments(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[RiskAssessmentResponse]:
        """Get risk assessment history for a customer."""
        query = self.db.query(RiskAssessment).filter(
            RiskAssessment.customer_id == customer_id
        )

        if start_date:
            query = query.filter(RiskAssessment.assessment_date >= start_date)
        if end_date:
            query = query.filter(RiskAssessment.assessment_date <= end_date)

        assessments = await query.order_by(RiskAssessment.assessment_date.desc()).all()
        return [
            RiskAssessmentResponse(
                id=assessment.id,
                customer_id=assessment.customer_id,
                risk_score=assessment.risk_score,
                risk_level=self._determine_risk_level(assessment.risk_score),
                assessment_date=assessment.assessment_date,
                details=assessment.details
            )
            for assessment in assessments
        ]

    async def get_assessment_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get statistical summary of risk assessments."""
        query = self.db.query(RiskAssessment)

        if start_date:
            query = query.filter(RiskAssessment.assessment_date >= start_date)
        if end_date:
            query = query.filter(RiskAssessment.assessment_date <= end_date)

        stats = await query.with_entities(
            func.count().label('total_assessments'),
            func.avg(RiskAssessment.risk_score).label('avg_risk_score'),
            func.min(RiskAssessment.risk_score).label('min_risk_score'),
            func.max(RiskAssessment.risk_score).label('max_risk_score')
        ).first()

        risk_level_distribution = await self._get_risk_level_distribution(query)

        return {
            "total_assessments": stats.total_assessments,
            "avg_risk_score": float(stats.avg_risk_score) if stats.avg_risk_score else 0,
            "min_risk_score": float(stats.min_risk_score) if stats.min_risk_score else 0,
            "max_risk_score": float(stats.max_risk_score) if stats.max_risk_score else 0,
            "risk_level_distribution": risk_level_distribution
        }

    def _calculate_factor_score(self, factor: RiskFactor, feature_value: any) -> float:
        """Calculate score for a single risk factor."""
        # Implementation depends on factor.operator and factor.threshold
        if factor.operator == "gt":
            return factor.weight if feature_value > factor.threshold else 0
        elif factor.operator == "lt":
            return factor.weight if feature_value < factor.threshold else 0
        elif factor.operator == "eq":
            return factor.weight if feature_value == factor.threshold else 0
        elif factor.operator == "in":
            return factor.weight if feature_value in factor.threshold else 0
        return 0

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on risk score."""
        if risk_score >= 80:
            return "HIGH"
        elif risk_score >= 50:
            return "MEDIUM"
        else:
            return "LOW"

    async def _get_risk_level_distribution(self, base_query) -> dict:
        """Get distribution of risk levels."""
        distribution = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        assessments = await base_query.all()
        for assessment in assessments:
            risk_level = self._determine_risk_level(assessment.risk_score)
            distribution[risk_level] += 1

        return distribution 