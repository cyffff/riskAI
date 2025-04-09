from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import logging
from fastapi import HTTPException, status
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

from ..models import SqlSet, SqlStatement, Feature, SqlType
from ..schemas import (
    SqlSetCreate, SqlSetUpdate,
    SqlStatementCreate, SqlStatementUpdate,
    SqlParseResult
)

logger = logging.getLogger(__name__)

class SqlService:
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
    ) -> List[SqlSet]:
        """Get SQL sets with filtering."""
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

            return query.offset(skip).limit(limit).all()
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

    async def create_sql_statement(
        self,
        sql_statement: SqlStatementCreate
    ) -> SqlStatement:
        """Create a new SQL statement."""
        try:
            # Parse SQL to extract metadata
            parse_result = await self.parse_sql(sql_statement.statement)
            
            db_sql_statement = SqlStatement(
                name=sql_statement.name,
                statement=sql_statement.statement,
                sql_type=sql_statement.sql_type,
                sql_set_id=sql_statement.sql_set_id,
                is_active=sql_statement.is_active,
                metadata=parse_result.metadata
            )
            self.db.add(db_sql_statement)
            await self.db.flush()
            return db_sql_statement
        except Exception as e:
            logger.error(f"Error creating SQL statement: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create SQL statement: {str(e)}"
            )

    async def get_sql_statements(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sql_set_id: Optional[int] = None,
        sql_type: Optional[SqlType] = None,
        is_active: Optional[bool] = None
    ) -> List[SqlStatement]:
        """Get SQL statements with filtering."""
        try:
            query = self.db.query(SqlStatement)

            if search:
                search_filter = or_(
                    SqlStatement.name.ilike(f"%{search}%"),
                    SqlStatement.statement.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)

            if sql_set_id:
                query = query.filter(SqlStatement.sql_set_id == sql_set_id)

            if sql_type:
                query = query.filter(SqlStatement.sql_type == sql_type)

            if is_active is not None:
                query = query.filter(SqlStatement.is_active == is_active)

            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting SQL statements: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL statements: {str(e)}"
            )

    async def get_sql_statement(self, sql_id: int) -> Optional[SqlStatement]:
        """Get a SQL statement by ID."""
        try:
            return self.db.query(SqlStatement).filter(SqlStatement.id == sql_id).first()
        except Exception as e:
            logger.error(f"Error getting SQL statement: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get SQL statement: {str(e)}"
            )

    async def update_sql_statement(
        self,
        sql_id: int,
        sql_statement: SqlStatementUpdate
    ) -> Optional[SqlStatement]:
        """Update a SQL statement."""
        try:
            db_sql_statement = await self.get_sql_statement(sql_id)
            if not db_sql_statement:
                return None

            update_data = sql_statement.dict(exclude_unset=True)
            
            # If statement is updated, parse it again
            if 'statement' in update_data:
                parse_result = await self.parse_sql(update_data['statement'])
                update_data['metadata'] = parse_result.metadata

            for field, value in update_data.items():
                setattr(db_sql_statement, field, value)

            await self.db.flush()
            return db_sql_statement
        except Exception as e:
            logger.error(f"Error updating SQL statement: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update SQL statement: {str(e)}"
            )

    async def delete_sql_statement(self, sql_id: int) -> bool:
        """Delete a SQL statement."""
        try:
            db_sql_statement = await self.get_sql_statement(sql_id)
            if not db_sql_statement:
                return False

            self.db.delete(db_sql_statement)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting SQL statement: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete SQL statement: {str(e)}"
            )

    async def parse_sql(self, sql: str) -> SqlParseResult:
        """Parse SQL statement to extract fields and metadata."""
        try:
            parsed = sqlparse.parse(sql)[0]
            fields = []
            metadata = {
                "tables": [],
                "type": None,
                "where_conditions": [],
                "joins": []
            }

            # Get statement type
            for token in parsed.tokens:
                if token.ttype is DML:
                    metadata["type"] = token.value.upper()
                    break

            # Extract fields from SELECT clause
            if metadata["type"] == "SELECT":
                select_idx = None
                from_idx = None
                
                for i, token in enumerate(parsed.tokens):
                    if token.ttype is DML and token.value.upper() == "SELECT":
                        select_idx = i
                    elif token.ttype is Keyword and token.value.upper() == "FROM":
                        from_idx = i
                        break

                if select_idx is not None and from_idx is not None:
                    select_tokens = parsed.tokens[select_idx + 1:from_idx]
                    for token in select_tokens:
                        if isinstance(token, IdentifierList):
                            for identifier in token.get_identifiers():
                                fields.append(str(identifier))
                        elif isinstance(token, Identifier):
                            fields.append(str(token))

            return SqlParseResult(
                fields=fields,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error parsing SQL: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse SQL: {str(e)}"
            ) 