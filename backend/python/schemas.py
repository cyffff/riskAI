from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class DataType(str, Enum):
    """Enumeration of supported feature data types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"

class Operator(str, Enum):
    """Enumeration of supported comparison operators."""
    GT = "gt"  # greater than
    LT = "lt"  # less than
    EQ = "eq"  # equal to
    GTE = "gte"  # greater than or equal
    LTE = "lte"  # less than or equal
    NE = "ne"  # not equal
    BETWEEN = "between"  # between two values

class RiskLevel(str, Enum):
    """Enumeration of risk levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SqlType(str, Enum):
    SIMPLE_QUERY = "SIMPLE_QUERY"
    POST_PROCESS_REQUIRED_QUERY = "POST_PROCESS_REQUIRED_QUERY"
    COMPLEX_QUERY = "COMPLEX_QUERY"

class FeatureType(str, Enum):
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    DATE = "DATE"
    SQL_FIELD = "SQL_FIELD"

class SqlSetBase(BaseModel):
    """Base Pydantic model for SQL Set data."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(True)

class SqlSetCreate(SqlSetBase):
    """Pydantic model for creating a new SQL Set."""
    pass

class SqlSetUpdate(SqlSetBase):
    """Pydantic model for updating an SQL Set."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class SqlSet(SqlSetBase):
    """Pydantic model for SQL Set response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SqlStatementBase(BaseModel):
    """Base Pydantic model for SQL Statement data."""
    name: str = Field(..., min_length=1, max_length=100)
    statement: str = Field(..., min_length=1, max_length=5000)
    sql_type: SqlType
    sql_set_id: int
    is_active: bool = Field(True)
    metadata: Optional[Dict[str, Any]] = None

class SqlStatementCreate(SqlStatementBase):
    """Pydantic model for creating a new SQL Statement."""
    pass

class SqlStatementUpdate(SqlStatementBase):
    """Pydantic model for updating an SQL Statement."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    statement: Optional[str] = Field(None, min_length=1, max_length=5000)
    sql_type: Optional[SqlType] = None
    sql_set_id: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class SqlStatement(SqlStatementBase):
    """Pydantic model for SQL Statement response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FeatureBase(BaseModel):
    """Base Pydantic model for Feature data."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    data_type: str = Field(..., description="Type of the feature data")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Data validation constraints")
    is_active: bool = Field(True, description="Whether the feature is active")
    importance_score: Optional[float] = Field(None, ge=0, le=1)
    category: Optional[str] = Field(None, max_length=50)
    computation_logic: Optional[str] = Field(None, max_length=1000)
    feature_type: FeatureType
    sql_set_id: Optional[int] = None
    sql_statement_id: Optional[int] = None
    field_name: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)

    @validator('data_type')
    def validate_data_type(cls, v):
        valid_types = ["numeric", "categorical", "boolean", "text", "date"]
        if v not in valid_types:
            raise ValueError(f"data_type must be one of {valid_types}")
        return v

    @validator('constraints')
    def validate_constraints(cls, v, values):
        if not v:
            return v
            
        data_type = values.get('data_type')
        if data_type == "numeric":
            if not all(key in v for key in ["min", "max"]):
                raise ValueError("Numeric features must have min and max constraints")
            if v["min"] > v["max"]:
                raise ValueError("min value cannot be greater than max value")
        elif data_type == "categorical":
            if "categories" not in v:
                raise ValueError("Categorical features must have categories defined")
            if not isinstance(v["categories"], list):
                raise ValueError("categories must be a list")
            if not v["categories"]:
                raise ValueError("categories cannot be empty")
        elif data_type == "text":
            if "max_length" not in v:
                raise ValueError("Text features must have max_length defined")
        
        return v

class FeatureCreate(FeatureBase):
    """Pydantic model for creating a new Feature."""
    pass

class FeatureUpdate(BaseModel):
    """Pydantic model for updating an existing Feature."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    data_type: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    importance_score: Optional[float] = Field(None, ge=0, le=1)
    category: Optional[str] = Field(None, max_length=50)
    computation_logic: Optional[str] = Field(None, max_length=1000)
    feature_type: Optional[FeatureType] = None
    sql_set_id: Optional[int] = None
    sql_statement_id: Optional[int] = None
    field_name: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None

    @validator('data_type')
    def validate_data_type(cls, v):
        if v is None:
            return v
        valid_types = ["numeric", "categorical", "boolean", "text", "date"]
        if v not in valid_types:
            raise ValueError(f"data_type must be one of {valid_types}")
        return v

class Feature(FeatureBase):
    """Pydantic model for Feature response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FeatureList(BaseModel):
    """Pydantic model for list of Features response."""
    items: List[Feature]
    total: int
    skip: int
    limit: int

class FeatureValidation(BaseModel):
    """Pydantic model for Feature validation response."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)

class RiskFactorBase(BaseModel):
    """Base model for risk factor data."""
    feature_id: int
    weight: float = Field(..., gt=0.0, le=1.0)
    threshold: float
    operator: Operator
    risk_level: RiskLevel
    description: str
    is_active: bool = True

class RiskFactorCreate(RiskFactorBase):
    """Model for creating a new risk factor."""
    pass

class RiskFactorUpdate(BaseModel):
    """Model for updating an existing risk factor."""
    weight: Optional[float] = Field(None, gt=0.0, le=1.0)
    threshold: Optional[float] = None
    operator: Optional[Operator] = None
    risk_level: Optional[RiskLevel] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RiskFactor(RiskFactorBase):
    """Model for risk factor response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RiskAssessmentRequest(BaseModel):
    """Model for risk assessment request."""
    customer_id: str
    features: Dict[str, Any] = Field(..., description="Feature values for assessment")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RiskAssessmentResponse(BaseModel):
    """Model for risk assessment response."""
    id: int
    customer_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    assessment_date: datetime
    factors: List[Dict[str, Any]] = Field(..., description="Contributing risk factors")
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    """Generic model for paginated responses."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

class FeatureValue(BaseModel):
    """Pydantic model for feature values."""
    feature_id: int
    entity_id: int
    value: Any

    class Config:
        orm_mode = True

class FeatureValueCreate(BaseModel):
    """Pydantic model for creating feature values."""
    entity_id: int
    value: Any

class FeatureValueUpdate(BaseModel):
    """Pydantic model for updating feature values."""
    value: Any

class FeatureValueResponse(FeatureValue):
    """Pydantic model for feature value response."""
    id: int
    created_at: datetime
    updated_at: datetime

class SqlParseResult(BaseModel):
    """Pydantic model for SQL parsing results."""
    fields: List[str]
    metadata: Dict[str, Any]

class PageResponse(BaseModel):
    """Base Pydantic model for paginated responses."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int 