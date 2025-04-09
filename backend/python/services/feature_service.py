from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import logging
from uuid import uuid4
import httpx
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from ..models import Feature, Tag, FeatureValue
from ..config import settings
from ..schemas import FeatureCreate, FeatureUpdate, FeatureValidation, FeatureValueCreate, FeatureValueUpdate

logger = logging.getLogger(__name__)

class FeatureService:
    def __init__(self, db: Session):
        self.db = db
        self.api_url = settings.FEATURE_API_URL
        self.api_key = settings.FEATURE_API_KEY
        self.timeout = settings.FEATURE_API_TIMEOUT

    async def get_features(self, page: int = 1, page_size: int = 10) -> Dict:
        """
        Get features from the Feature Management API.
        
        Args:
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Dictionary containing features and pagination info
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/feature/management/features",
                    params={
                        "page": page,
                        "pageSize": page_size
                    },
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching features: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail="Error fetching features from Feature Management API")
        except Exception as e:
            logger.error(f"Error fetching features: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def create_feature(self, feature: FeatureCreate) -> Feature:
        """Create a new feature with tags."""
        try:
            # Create tags if they don't exist
            tags = []
            for tag_name in feature.tags:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                tags.append(tag)
            
            # Create feature
            db_feature = Feature(
                name=feature.name,
                description=feature.description,
                data_type=feature.data_type,
                constraints=feature.constraints,
                is_active=feature.is_active,
                importance_score=feature.importance_score,
                category=feature.category,
                computation_logic=feature.computation_logic,
                tags=tags
            )
            
            self.db.add(db_feature)
            await self.db.flush()
            return db_feature
        except Exception as e:
            logger.error(f"Error creating feature: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create feature: {str(e)}"
            )

    async def update_feature(
        self,
        feature_id: int,
        feature_update: FeatureUpdate
    ) -> Optional[Feature]:
        """Update a feature."""
        try:
            db_feature = await self.get_feature(feature_id)
            if not db_feature:
                return None

            # Update tags if provided
            if feature_update.tags is not None:
                tags = []
                for tag_name in feature_update.tags:
                    tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        self.db.add(tag)
                    tags.append(tag)
                db_feature.tags = tags

            # Update other fields
            update_data = feature_update.dict(exclude_unset=True)
            update_data.pop('tags', None)  # Remove tags as they're handled separately
            
            for field, value in update_data.items():
                setattr(db_feature, field, value)

            await self.db.flush()
            return db_feature
        except Exception as e:
            logger.error(f"Error updating feature: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update feature: {str(e)}"
            )

    async def get_feature_importance(self) -> List[Dict]:
        """
        Get feature importance information.
        This is a mock implementation since it's not available in the Feature Management API.
        """
        return [
            {"name": "credit_history", "importance": 0.35},
            {"name": "income_level", "importance": 0.25},
            {"name": "payment_behavior", "importance": 0.20},
            {"name": "debt_ratio", "importance": 0.15},
            {"name": "employment_status", "importance": 0.05}
        ]

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def delete_feature(self, feature_id: int) -> bool:
        """Soft delete a feature."""
        try:
            db_feature = await self.get_feature(feature_id)
            if not db_feature:
                return False

            db_feature.is_active = False
            db_feature.updated_at = datetime.utcnow()
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting feature: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete feature: {str(e)}"
            )

    async def get_feature_metrics(self, feature_id: str) -> Dict:
        """
        Get metrics for a specific feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            Dictionary containing feature metrics
        """
        try:
            feature = self.db.query(Feature).filter(Feature.id == feature_id).first()
            if not feature:
                raise ValueError(f"Feature {feature_id} not found")
            
            # Get metrics from feature system API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/features/{feature_id}/metrics",
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting metrics for feature {feature_id}: {e}")
            raise

    def _validate_feature_data(self, feature_data: Dict) -> None:
        """Validate feature data."""
        required_fields = ["name", "description", "computation_logic"]
        
        for field in required_fields:
            if field not in feature_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not feature_data["name"].strip():
            raise ValueError("Feature name cannot be empty")
        
        if not feature_data["computation_logic"].strip():
            raise ValueError("Computation logic cannot be empty")

    async def _register_feature_with_api(self, feature: Feature) -> None:
        """Register feature with feature system API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/features",
                    headers=self._get_headers(),
                    json={
                        "id": feature.id,
                        "name": feature.name,
                        "description": feature.description,
                        "computation_logic": feature.computation_logic
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error registering feature with API: {e}")
            raise

    async def _update_feature_in_api(self, feature: Feature) -> None:
        """Update feature in feature system API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.api_url}/features/{feature.id}",
                    headers=self._get_headers(),
                    json={
                        "name": feature.name,
                        "description": feature.description,
                        "computation_logic": feature.computation_logic
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error updating feature in API: {e}")
            raise

    async def _remove_feature_from_api(self, feature_id: str) -> None:
        """Remove feature from feature system API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.api_url}/features/{feature_id}",
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error removing feature from API: {e}")
            raise

    @staticmethod
    async def get_features(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[Feature]:
        """
        Get features with filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for name or description
            category: Filter by category
            is_active: Filter by active status
            tags: Filter by tags
            
        Returns:
            List of features matching the criteria
        """
        query = db.query(Feature)

        # Apply filters
        if search:
            search_filter = or_(
                Feature.name.ilike(f"%{search}%"),
                Feature.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        if category:
            query = query.filter(Feature.category == category)

        if is_active is not None:
            query = query.filter(Feature.is_active == is_active)

        if tags:
            query = query.filter(Feature.tags.any(Tag.name.in_(tags)))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    async def get_feature_by_id(db: Session, feature_id: int) -> Feature:
        """
        Retrieve a feature by its ID.
        
        Args:
            db: Database session
            feature_id: ID of the feature to retrieve
            
        Returns:
            Feature object
            
        Raises:
            HTTPException: If feature is not found
        """
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with ID {feature_id} not found"
            )
        return feature

    @staticmethod
    async def get_feature_by_name(db: Session, name: str) -> Feature:
        """
        Retrieve a feature by its name.
        
        Args:
            db: Database session
            name: Name of the feature to retrieve
            
        Returns:
            Feature object
            
        Raises:
            HTTPException: If feature is not found
        """
        feature = db.query(Feature).filter(Feature.name == name).first()
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with name '{name}' not found"
            )
        return feature

    @staticmethod
    async def create_feature(db: Session, feature: FeatureCreate) -> Feature:
        """
        Create a new feature.
        
        Args:
            db: Database session
            feature: Feature creation data
            
        Returns:
            Created feature instance
        """
        # Create tags if they don't exist
        tags = []
        for tag_name in feature.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            tags.append(tag)
        
        # Create feature
        db_feature = Feature(
            name=feature.name,
            description=feature.description,
            data_type=feature.data_type,
            constraints=feature.constraints,
            is_active=feature.is_active,
            importance_score=feature.importance_score,
            category=feature.category,
            tags=tags
        )
        
        db.add(db_feature)
        await db.flush()
        return db_feature

    @staticmethod
    async def update_feature(
        db: Session,
        feature_id: int,
        feature_update: FeatureUpdate
    ) -> Optional[Feature]:
        """
        Update a feature.
        
        Args:
            db: Database session
            feature_id: ID of the feature to update
            feature_update: Update data
            
        Returns:
            Updated feature instance if found, None otherwise
        """
        db_feature = await FeatureService.get_feature(db, feature_id)
        if not db_feature:
            return None

        # Update tags if provided
        if feature_update.tags is not None:
            tags = []
            for tag_name in feature_update.tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                tags.append(tag)
            db_feature.tags = tags

        # Update other fields
        update_data = feature_update.dict(exclude_unset=True)
        update_data.pop('tags', None)  # Remove tags as they're handled separately
        
        for field, value in update_data.items():
            setattr(db_feature, field, value)

        await db.flush()
        return db_feature

    @staticmethod
    async def delete_feature(db: Session, feature_id: int) -> bool:
        """
        Delete a feature.
        
        Args:
            db: Database session
            feature_id: ID of the feature to delete
            
        Returns:
            True if feature was deleted, False if not found
        """
        db_feature = await FeatureService.get_feature(db, feature_id)
        if not db_feature:
            return False

        db.delete(db_feature)
        await db.flush()
        return True

    @staticmethod
    async def validate_feature(db: Session, feature_id: int) -> FeatureValidation:
        """
        Validate a feature's configuration.
        
        Args:
            db: Database session
            feature_id: ID of the feature to validate
            
        Returns:
            FeatureValidation object
        """
        db_feature = await FeatureService.get_feature_by_id(db, feature_id)
        errors = []
        
        # Validate data type
        valid_data_types = ["numeric", "categorical", "boolean", "text", "date"]
        if db_feature.data_type not in valid_data_types:
            errors.append(f"Invalid data type: {db_feature.data_type}")
        
        # Validate constraints based on data type
        if db_feature.constraints:
            if db_feature.data_type == "numeric":
                if not all(key in db_feature.constraints for key in ["min", "max"]):
                    errors.append("Numeric features must have min and max constraints")
            elif db_feature.data_type == "categorical":
                if "categories" not in db_feature.constraints:
                    errors.append("Categorical features must have categories defined")
        
        return FeatureValidation(
            is_valid=len(errors) == 0,
            errors=errors
        )

    @staticmethod
    async def validate_feature_value(
        db: Session,
        feature_id: int,
        value: Any
    ) -> FeatureValidation:
        """
        Validate a value against a feature's constraints.
        
        Args:
            db: Database session
            feature_id: ID of the feature to validate against
            value: Value to validate
            
        Returns:
            Validation result
        """
        feature = await FeatureService.get_feature(db, feature_id)
        if not feature:
            return FeatureValidation(is_valid=False, errors=["Feature not found"])

        errors = []

        # Validate based on data type
        if feature.data_type == "numeric":
            if not isinstance(value, (int, float)):
                errors.append("Value must be numeric")
            else:
                min_val = feature.constraints.get("min")
                max_val = feature.constraints.get("max")
                if min_val is not None and value < min_val:
                    errors.append(f"Value must be greater than or equal to {min_val}")
                if max_val is not None and value > max_val:
                    errors.append(f"Value must be less than or equal to {max_val}")

        elif feature.data_type == "categorical":
            categories = feature.constraints.get("categories", [])
            if value not in categories:
                errors.append(f"Value must be one of: {', '.join(categories)}")

        elif feature.data_type == "boolean":
            if not isinstance(value, bool):
                errors.append("Value must be a boolean")

        elif feature.data_type == "text":
            if not isinstance(value, str):
                errors.append("Value must be a string")
            else:
                max_length = feature.constraints.get("max_length")
                if max_length and len(value) > max_length:
                    errors.append(f"Text length must be less than or equal to {max_length}")

        elif feature.data_type == "date":
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("Value must be a valid ISO format date string")

        return FeatureValidation(is_valid=len(errors) == 0, errors=errors)

    @staticmethod
    async def set_feature_value(
        db: Session,
        feature_id: int,
        value_data: FeatureValueCreate
    ) -> FeatureValue:
        """Set a value for a feature-entity combination."""
        try:
            # Validate the value first
            validation = await FeatureService.validate_feature_value(db, feature_id, value_data.value)
            if not validation.is_valid:
                raise ValueError(f"Invalid value: {', '.join(validation.errors)}")

            # Get or create feature value
            feature_value = db.query(FeatureValue).filter(
                and_(
                    FeatureValue.feature_id == feature_id,
                    FeatureValue.entity_id == value_data.entity_id
                )
            ).first()

            if feature_value:
                feature_value.value = value_data.value
                feature_value.updated_at = datetime.utcnow()
            else:
                feature_value = FeatureValue(
                    feature_id=feature_id,
                    entity_id=value_data.entity_id,
                    value=value_data.value
                )
                db.add(feature_value)

            await db.flush()
            return feature_value
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error setting feature value: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set feature value: {str(e)}"
            )

    async def get_feature_values(
        self,
        feature_id: int,
        entity_ids: Optional[List[int]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FeatureValue]:
        """Get feature values with optional filtering by entity IDs."""
        try:
            query = self.db.query(FeatureValue).filter(FeatureValue.feature_id == feature_id)
            
            if entity_ids:
                query = query.filter(FeatureValue.entity_id.in_(entity_ids))
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting feature values: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get feature values: {str(e)}"
            ) 