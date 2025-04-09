from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import ModelAdjustment
from config import FEATURE_API_URL, FEATURE_API_HEADERS
import requests

class ModelService:
    def __init__(self, db: Session):
        self.db = db

    def get_model_metrics(self) -> Dict:
        """
        Get current model performance metrics
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/model/metrics",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching model metrics: {e}")
            return {}

    def get_model_cutoff(self) -> float:
        """
        Get current model cutoff threshold
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/model/cutoff",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()["cutoff"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching model cutoff: {e}")
            return 0.5  # Default cutoff

    def update_model_cutoff(self, new_cutoff: float) -> bool:
        """
        Update model cutoff threshold
        """
        try:
            response = requests.post(
                f"{FEATURE_API_URL}/model/cutoff",
                headers=FEATURE_API_HEADERS,
                json={"cutoff": new_cutoff}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating model cutoff: {e}")
            return False

    def get_model_predictions(self, user_ids: List[str]) -> Dict[str, float]:
        """
        Get model predictions for multiple users
        """
        try:
            response = requests.post(
                f"{FEATURE_API_URL}/model/predict",
                headers=FEATURE_API_HEADERS,
                json={"user_ids": user_ids}
            )
            response.raise_for_status()
            return response.json()["predictions"]
        except requests.exceptions.RequestException as e:
            print(f"Error getting model predictions: {e}")
            return {}

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from the model
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/model/feature-importance",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()["importance"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feature importance: {e}")
            return {}

    def simulate_cutoff_change(self, new_cutoff: float) -> Dict:
        """
        Simulate the impact of changing the model cutoff
        """
        try:
            response = requests.post(
                f"{FEATURE_API_URL}/model/simulate-cutoff",
                headers=FEATURE_API_HEADERS,
                json={"cutoff": new_cutoff}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error simulating cutoff change: {e}")
            return {}

    def record_model_adjustment(self, adjustment_data: Dict) -> ModelAdjustment:
        """
        Record a model adjustment in the database
        """
        adjustment = ModelAdjustment(
            previous_cutoff=adjustment_data["previous_cutoff"],
            new_cutoff=adjustment_data["new_cutoff"],
            expected_improvements=adjustment_data["expected_improvements"],
            rationale=adjustment_data["rationale"]
        )
        self.db.add(adjustment)
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def get_adjustment_history(self) -> List[ModelAdjustment]:
        """
        Get history of model adjustments
        """
        return self.db.query(ModelAdjustment).order_by(ModelAdjustment.adjustment_date.desc()).all()

    def get_model_performance_trends(self, days: int = 30) -> Dict:
        """
        Get model performance trends over time
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/model/performance-trends",
                headers=FEATURE_API_HEADERS,
                params={"days": days}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching performance trends: {e}")
            return {} 