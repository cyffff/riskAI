from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
from uuid import uuid4
from datetime import datetime
import httpx

from ..models import ModelAdjustment, ModelMetrics
from ..config import settings

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self.feature_api_url = settings.FEATURE_API_URL
        self.feature_api_key = settings.FEATURE_API_KEY

    async def get_model_metrics(self, period: str = "30d") -> Dict:
        """
        Get model performance metrics.
        
        Args:
            period: Time period for metrics (e.g., "30d", "90d", "1y")
            
        Returns:
            Dictionary containing model metrics
        """
        try:
            # Get metrics from database
            metrics = (
                self.db.query(ModelMetrics)
                .filter(ModelMetrics.period == period)
                .order_by(ModelMetrics.evaluation_date.desc())
                .all()
            )
            
            # Get current model cutoff
            current_cutoff = await self._get_model_cutoff()
            
            return {
                "current_cutoff": current_cutoff,
                "metrics": [
                    {
                        "name": m.metric_name,
                        "value": m.metric_value,
                        "evaluation_date": m.evaluation_date.isoformat(),
                        "period": m.period,
                        "metadata": m.metadata
                    }
                    for m in metrics
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching model metrics: {e}")
            raise

    async def record_model_adjustment(self, adjustment_data: Dict) -> Dict:
        """
        Record a model adjustment.
        
        Args:
            adjustment_data: Dictionary containing adjustment information
            
        Returns:
            Created adjustment record
        """
        try:
            # Validate adjustment data
            self._validate_adjustment_data(adjustment_data)
            
            # Get current model state
            current_state = await self._get_model_state()
            
            # Create adjustment record
            adjustment = ModelAdjustment(
                id=str(uuid4()),
                adjustment_type=adjustment_data["type"],
                previous_value=current_state,
                new_value=adjustment_data["new_value"],
                rationale=adjustment_data["rationale"],
                expected_impact=adjustment_data["expected_impact"],
                created_by=adjustment_data["created_by"],
                status="pending"
            )
            
            self.db.add(adjustment)
            self.db.commit()
            self.db.refresh(adjustment)
            
            # Apply adjustment in feature system API
            await self._apply_model_adjustment(adjustment)
            
            return {
                "id": adjustment.id,
                "type": adjustment.adjustment_type,
                "previous_value": adjustment.previous_value,
                "new_value": adjustment.new_value,
                "rationale": adjustment.rationale,
                "expected_impact": adjustment.expected_impact,
                "created_by": adjustment.created_by,
                "status": adjustment.status,
                "created_at": adjustment.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording model adjustment: {e}")
            self.db.rollback()
            raise

    async def get_model_cutoff(self) -> float:
        """
        Get current model cutoff threshold.
        
        Returns:
            Current cutoff value
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.feature_api_url}/model/cutoff",
                    headers={"Authorization": f"Bearer {self.feature_api_key}"}
                )
                response.raise_for_status()
                return response.json()["cutoff"]
                
        except Exception as e:
            logger.error(f"Error getting model cutoff: {e}")
            raise

    async def update_model_cutoff(self, new_cutoff: float, rationale: str, created_by: str) -> Dict:
        """
        Update model cutoff threshold.
        
        Args:
            new_cutoff: New cutoff value
            rationale: Reason for the change
            created_by: User making the change
            
        Returns:
            Created adjustment record
        """
        try:
            current_cutoff = await self._get_model_cutoff()
            
            adjustment_data = {
                "type": "cutoff",
                "new_value": {"cutoff": new_cutoff},
                "rationale": rationale,
                "expected_impact": await self._simulate_cutoff_change(current_cutoff, new_cutoff),
                "created_by": created_by
            }
            
            return await self.record_model_adjustment(adjustment_data)
            
        except Exception as e:
            logger.error(f"Error updating model cutoff: {e}")
            raise

    async def get_adjustment_history(self, limit: int = 10) -> List[Dict]:
        """
        Get history of model adjustments.
        
        Args:
            limit: Maximum number of adjustments to return
            
        Returns:
            List of adjustment records
        """
        try:
            adjustments = (
                self.db.query(ModelAdjustment)
                .order_by(ModelAdjustment.created_at.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "id": a.id,
                    "type": a.adjustment_type,
                    "previous_value": a.previous_value,
                    "new_value": a.new_value,
                    "rationale": a.rationale,
                    "expected_impact": a.expected_impact,
                    "created_by": a.created_by,
                    "status": a.status,
                    "created_at": a.created_at.isoformat()
                }
                for a in adjustments
            ]
            
        except Exception as e:
            logger.error(f"Error fetching adjustment history: {e}")
            raise

    async def _get_model_state(self) -> Dict:
        """Get current model state from feature system API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.feature_api_url}/model/state",
                    headers={"Authorization": f"Bearer {self.feature_api_key}"}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting model state: {e}")
            raise

    async def _apply_model_adjustment(self, adjustment: ModelAdjustment) -> None:
        """Apply model adjustment in feature system API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.feature_api_url}/model/adjustments",
                    headers={"Authorization": f"Bearer {self.feature_api_key}"},
                    json={
                        "id": adjustment.id,
                        "type": adjustment.adjustment_type,
                        "new_value": adjustment.new_value,
                        "expected_impact": adjustment.expected_impact
                    }
                )
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error applying model adjustment: {e}")
            raise

    async def _simulate_cutoff_change(self, current_cutoff: float, new_cutoff: float) -> Dict:
        """Simulate impact of cutoff change."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.feature_api_url}/model/simulate-cutoff",
                    headers={"Authorization": f"Bearer {self.feature_api_key}"},
                    json={
                        "current_cutoff": current_cutoff,
                        "new_cutoff": new_cutoff
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error simulating cutoff change: {e}")
            raise

    def _validate_adjustment_data(self, adjustment_data: Dict) -> None:
        """Validate adjustment data."""
        required_fields = ["type", "new_value", "rationale", "expected_impact", "created_by"]
        
        for field in required_fields:
            if field not in adjustment_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not adjustment_data["rationale"].strip():
            raise ValueError("Rationale cannot be empty")
        
        if not adjustment_data["created_by"].strip():
            raise ValueError("Created by cannot be empty") 