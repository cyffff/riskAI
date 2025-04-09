from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.sql_service import SqlService
from ..models import SqlType
from ..schemas import (
    SqlSet, SqlSetCreate, SqlSetUpdate,
    SqlStatement, SqlStatementCreate, SqlStatementUpdate,
    SqlParseResult, PageResponse
)

router = APIRouter(prefix="/api/v1/sql", tags=["sql"])

# SQL Set endpoints
@router.post("/sets", response_model=SqlSet)
async def create_sql_set(
    sql_set: SqlSetCreate,
    db: Session = Depends(get_db)
):
    """Create a new SQL set."""
    service = SqlService(db)
    return await service.create_sql_set(sql_set)

@router.get("/sets", response_model=List[SqlSet])
async def get_sql_sets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get SQL sets with filtering."""
    service = SqlService(db)
    return await service.get_sql_sets(
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )

@router.get("/sets/{sql_set_id}", response_model=SqlSet)
async def get_sql_set(
    sql_set_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific SQL set by ID."""
    service = SqlService(db)
    sql_set = await service.get_sql_set(sql_set_id)
    if not sql_set:
        raise HTTPException(status_code=404, detail="SQL set not found")
    return sql_set

@router.put("/sets/{sql_set_id}", response_model=SqlSet)
async def update_sql_set(
    sql_set_id: int,
    sql_set: SqlSetUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific SQL set."""
    service = SqlService(db)
    updated_sql_set = await service.update_sql_set(sql_set_id, sql_set)
    if not updated_sql_set:
        raise HTTPException(status_code=404, detail="SQL set not found")
    return updated_sql_set

@router.delete("/sets/{sql_set_id}")
async def delete_sql_set(
    sql_set_id: int,
    db: Session = Depends(get_db)
):
    """Delete a SQL set."""
    service = SqlService(db)
    if not await service.delete_sql_set(sql_set_id):
        raise HTTPException(status_code=404, detail="SQL set not found")
    return {"message": "SQL set deleted successfully"}

# SQL Statement endpoints
@router.post("/statements", response_model=SqlStatement)
async def create_sql_statement(
    sql_statement: SqlStatementCreate,
    db: Session = Depends(get_db)
):
    """Create a new SQL statement."""
    service = SqlService(db)
    return await service.create_sql_statement(sql_statement)

@router.get("/statements", response_model=List[SqlStatement])
async def get_sql_statements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    sql_set_id: Optional[int] = None,
    sql_type: Optional[SqlType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get SQL statements with filtering."""
    service = SqlService(db)
    return await service.get_sql_statements(
        skip=skip,
        limit=limit,
        search=search,
        sql_set_id=sql_set_id,
        sql_type=sql_type,
        is_active=is_active
    )

@router.get("/statements/{sql_id}", response_model=SqlStatement)
async def get_sql_statement(
    sql_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific SQL statement by ID."""
    service = SqlService(db)
    sql_statement = await service.get_sql_statement(sql_id)
    if not sql_statement:
        raise HTTPException(status_code=404, detail="SQL statement not found")
    return sql_statement

@router.put("/statements/{sql_id}", response_model=SqlStatement)
async def update_sql_statement(
    sql_id: int,
    sql_statement: SqlStatementUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific SQL statement."""
    service = SqlService(db)
    updated_sql_statement = await service.update_sql_statement(sql_id, sql_statement)
    if not updated_sql_statement:
        raise HTTPException(status_code=404, detail="SQL statement not found")
    return updated_sql_statement

@router.delete("/statements/{sql_id}")
async def delete_sql_statement(
    sql_id: int,
    db: Session = Depends(get_db)
):
    """Delete a SQL statement."""
    service = SqlService(db)
    if not await service.delete_sql_statement(sql_id):
        raise HTTPException(status_code=404, detail="SQL statement not found")
    return {"message": "SQL statement deleted successfully"}

@router.post("/statements/parse", response_model=SqlParseResult)
async def parse_sql(
    statement: str,
    db: Session = Depends(get_db)
):
    """Parse a SQL statement to extract fields and metadata."""
    service = SqlService(db)
    return await service.parse_sql(statement) 