from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Feature
from config import FEATURE_API_URL, FEATURE_API_HEADERS
import requests
from datetime import datetime

from ..schemas import FeatureCreate, FeatureUpdate

class FeatureService:
    def __init__(self, db: Session):
        self.db = db

    def list_features(self) -> List[Dict]:
        """
        List all available features
        """
        features = self.db.query(Feature).all()
        return [
            {
                "name": feature.name,
                "type": feature.feature_type,
                "description": feature.description,
                "computation_logic": feature.computation_logic
            }
            for feature in features
        ]

    def get_feature_value(self, user_id: str, feature_name: str) -> Optional[float]:
        """
        Get feature value for a specific user
        """
        try:
            # Call feature system API
            response = requests.get(
                f"{FEATURE_API_URL}/features/{feature_name}/users/{user_id}",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()["value"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feature value: {e}")
            return None

    def compute_features(self, user_id: str, feature_names: List[str]) -> Dict[str, float]:
        """
        Compute multiple features for a user
        """
        results = {}
        for feature_name in feature_names:
            value = self.get_feature_value(user_id, feature_name)
            if value is not None:
                results[feature_name] = value
        return results

    def add_feature(self, feature_data: Dict) -> Feature:
        """
        Add a new feature to the system
        """
        feature = Feature(
            name=feature_data["name"],
            description=feature_data["description"],
            computation_logic=feature_data["computation_logic"],
            feature_type=feature_data["type"]
        )
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        return feature

    def update_feature(self, feature_name: str, feature_data: Dict) -> Optional[Feature]:
        """
        Update an existing feature
        """
        feature = self.db.query(Feature).filter(Feature.name == feature_name).first()
        if feature:
            for key, value in feature_data.items():
                setattr(feature, key, value)
            self.db.commit()
            self.db.refresh(feature)
        return feature

    def delete_feature(self, feature_name: str) -> bool:
        """
        Delete a feature from the system
        """
        feature = self.db.query(Feature).filter(Feature.name == feature_name).first()
        if feature:
            self.db.delete(feature)
            self.db.commit()
            return True
        return False

    def get_feature_importance(self, feature_name: str) -> Optional[float]:
        """
        Get feature importance score from the model
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/features/{feature_name}/importance",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()["importance"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feature importance: {e}")
            return None

    def get_feature_correlations(self, feature_name: str) -> Dict[str, float]:
        """
        Get correlations between a feature and other features
        """
        try:
            response = requests.get(
                f"{FEATURE_API_URL}/features/{feature_name}/correlations",
                headers=FEATURE_API_HEADERS
            )
            response.raise_for_status()
            return response.json()["correlations"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feature correlations: {e}")
            return {}

    async def create_feature(self, feature: FeatureCreate) -> Feature:
        """Create a new feature."""
        db_feature = Feature(**feature.dict())
        self.db.add(db_feature)
        await self.db.commit()
        await self.db.refresh(db_feature)
        return db_feature

    async def get_feature(self, feature_id: int) -> Optional[Feature]:
        """Get a feature by ID."""
        return await self.db.query(Feature).filter(Feature.id == feature_id).first()

    async def list_features(
        self,
        page: int,
        page_size: int,
        data_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """List features with pagination and filtering."""
        query = self.db.query(Feature)

        # Apply filters
        if data_type:
            query = query.filter(Feature.data_type == data_type)
        if is_active is not None:
            query = query.filter(Feature.is_active == is_active)
        if search:
            search_filter = or_(
                Feature.name.ilike(f"%{search}%"),
                Feature.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count for pagination
        total = await query.count()

        # Apply pagination
        features = await query.order_by(Feature.name).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return {
            "items": features,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_feature(
        self,
        feature_id: int,
        feature: FeatureUpdate
    ) -> Optional[Feature]:
        """Update a feature."""
        db_feature = await self.get_feature(feature_id)
        if not db_feature:
            return None

        # Update only provided fields
        for field, value in feature.dict(exclude_unset=True).items():
            setattr(db_feature, field, value)

        await self.db.commit()
        await self.db.refresh(db_feature)
        return db_feature

    async def delete_feature(self, feature_id: int) -> bool:
        """Delete a feature (soft delete by setting is_active to False)."""
        db_feature = await self.get_feature(feature_id)
        if not db_feature:
            return False

        db_feature.is_active = False
        await self.db.commit()
        return True

    async def validate_feature_values(
        self,
        feature_id: int,
        values: List[any]
    ) -> dict:
        """Validate a list of values against a feature's constraints."""
        feature = await self.get_feature(feature_id)
        if not feature:
            return {
                "is_valid": False,
                "errors": ["Feature not found"]
            }

        errors = []
        for value in values:
            # Validate data type
            if not self._validate_data_type(value, feature.data_type):
                errors.append(f"Value {value} does not match data type {feature.data_type}")

            # Validate constraints if any
            if feature.constraints:
                constraint_errors = self._validate_constraints(value, feature.constraints)
                errors.extend(constraint_errors)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def _validate_data_type(self, value: any, data_type: str) -> bool:
        """Validate if a value matches the expected data type."""
        try:
            if data_type == "numeric":
                float(value)
            elif data_type == "boolean":
                isinstance(value, bool)
            elif data_type == "string":
                str(value)
            elif data_type == "date":
                datetime.fromisoformat(str(value))
            elif data_type == "categorical":
                str(value)
            else:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def _validate_constraints(self, value: any, constraints: dict) -> List[str]:
        """Validate if a value meets the defined constraints."""
        errors = []

        if not constraints:
            return errors

        # Numeric constraints
        if "min" in constraints and value < constraints["min"]:
            errors.append(f"Value {value} is less than minimum {constraints['min']}")
        if "max" in constraints and value > constraints["max"]:
            errors.append(f"Value {value} is greater than maximum {constraints['max']}")

        # String constraints
        if "min_length" in constraints and len(str(value)) < constraints["min_length"]:
            errors.append(
                f"Value length {len(str(value))} is less than minimum length {constraints['min_length']}"
            )
        if "max_length" in constraints and len(str(value)) > constraints["max_length"]:
            errors.append(
                f"Value length {len(str(value))} is greater than maximum length {constraints['max_length']}"
            )

        # Categorical constraints
        if "allowed_values" in constraints and value not in constraints["allowed_values"]:
            errors.append(f"Value {value} is not in allowed values: {constraints['allowed_values']}")

        # Pattern constraint
        if "pattern" in constraints:
            import re
            if not re.match(constraints["pattern"], str(value)):
                errors.append(f"Value {value} does not match pattern {constraints['pattern']}")

        return errors 