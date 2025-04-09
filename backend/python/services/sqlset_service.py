from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import logging
from fastapi import HTTPException, status

from ..models import SqlSet, SqlStatement, Feature
from ..schemas import (
    SqlSetCreate, SqlSetUpdate,
    PageResponse
)

logger = logging.getLogger(__name__)

class SqlSetService:
    def __init__(self, db: Session):
        self.db = db

    async def create_sql_set(self, sql_set: SqlSetCreate) -> SqlSet:
        """Create a new SQL set."""
        try:
            db_sql_set = SqlSet(
                name=sql_set.name,
                description=sql_set.description,
                is_active=sql_set.is_active
            )
            self.db.add(db_sql_set)
            await self.db.flush()
            return db_sql_set
        except Exception as e:
            logger.error(f"Error creating SQL set: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create SQL set: {str(e)}"
            )

    async def get_sql_sets(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[SqlSet], int]:
        """
        Get SQL sets with filtering and return total count for pagination.
        
        Returns:
            Tuple containing list of SQL sets and total count
        """
        try:
            query = self.db.query(SqlSet)

            if search:
                search_filter = or_(
                    SqlSet.name.ilike(f"%{search}%"),
                    SqlSet.description.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)

            if is_active is not None:
                query = query.filter(SqlSet.is_active == is_active)
                
            # Get total count for pagination
            total_count = query.count()
            
            # Apply pagination
            sql_sets = query.order_by(SqlSet.name).offset(skip).limit(limit).all()
            
            return sql_sets, total_count
        except Exception as e:
            logger.error(f"Error getting SQL sets: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL sets: {str(e)}"
            )

    async def get_sql_set(self, sql_set_id: int) -> Optional[SqlSet]:
        """Get a SQL set by ID."""
        try:
            return self.db.query(SqlSet).filter(SqlSet.id == sql_set_id).first()
        except Exception as e:
            logger.error(f"Error getting SQL set: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL set: {str(e)}"
            )

    async def update_sql_set(
        self,
        sql_set_id: int,
        sql_set: SqlSetUpdate
    ) -> Optional[SqlSet]:
        """Update a SQL set."""
        try:
            db_sql_set = await self.get_sql_set(sql_set_id)
            if not db_sql_set:
                return None

            update_data = sql_set.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_sql_set, field, value)

            await self.db.flush()
            return db_sql_set
        except Exception as e:
            logger.error(f"Error updating SQL set: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update SQL set: {str(e)}"
            )

    async def delete_sql_set(self, sql_set_id: int) -> bool:
        """Delete a SQL set."""
        try:
            db_sql_set = await self.get_sql_set(sql_set_id)
            if not db_sql_set:
                return False

            self.db.delete(db_sql_set)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting SQL set: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete SQL set: {str(e)}"
            )
    
    async def get_sql_set_features(
        self, 
        sql_set_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[Feature], int]:
        """
        Get features associated with a specific SQL set.
        
        Args:
            sql_set_id: ID of the SQL set
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for filtering features
            
        Returns:
            Tuple containing list of features and total count
        """
        try:
            query = self.db.query(Feature).filter(Feature.sql_set_id == sql_set_id)
            
            if search:
                search_filter = or_(
                    Feature.name.ilike(f"%{search}%"),
                    Feature.description.ilike(f"%{search}%"),
                    Feature.category.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
                
            # Get total count for pagination
            total_count = query.count()
            
            # Apply pagination
            features = query.order_by(Feature.name).offset(skip).limit(limit).all()
            
            return features, total_count
        except Exception as e:
            logger.error(f"Error getting SQL set features: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL set features: {str(e)}"
            )
    
    async def get_sql_set_stats(self, sql_set_id: int) -> Dict[str, Any]:
        """
        Get statistics for a SQL set, including:
        - Total number of features
        - Number of active features
        - Number of SQL statements
        - Feature types distribution
        
        Args:
            sql_set_id: ID of the SQL set
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Get SQL set
            sql_set = await self.get_sql_set(sql_set_id)
            if not sql_set:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SQL set with ID {sql_set_id} not found"
                )
            
            # Count features
            feature_count = self.db.query(func.count(Feature.id)).filter(
                Feature.sql_set_id == sql_set_id
            ).scalar()
            
            # Count active features
            active_feature_count = self.db.query(func.count(Feature.id)).filter(
                and_(
                    Feature.sql_set_id == sql_set_id,
                    Feature.is_active == True
                )
            ).scalar()
            
            # Count SQL statements
            sql_statement_count = self.db.query(func.count(SqlStatement.id)).filter(
                SqlStatement.sql_set_id == sql_set_id
            ).scalar()
            
            # Get feature type distribution
            feature_types = self.db.query(
                Feature.feature_type,
                func.count(Feature.id).label("count")
            ).filter(
                Feature.sql_set_id == sql_set_id
            ).group_by(Feature.feature_type).all()
            
            feature_type_distribution = {
                str(ft_type): count for ft_type, count in feature_types
            }
            
            return {
                "total_features": feature_count,
                "active_features": active_feature_count,
                "sql_statements": sql_statement_count,
                "feature_type_distribution": feature_type_distribution,
                "name": sql_set.name,
                "description": sql_set.description,
                "is_active": sql_set.is_active,
                "created_at": sql_set.created_at,
                "updated_at": sql_set.updated_at
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting SQL set statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL set statistics: {str(e)}"
            ) 