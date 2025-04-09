from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Risk metrics
    risk_score = Column(Float)
    risk_segment = Column(String(20))
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    credit_inquiries = relationship("CreditInquiry", back_populates="user")
    risk_analyses = relationship("RiskAnalysis", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(String(50))  # e.g., "purchase", "refund", "payment"
    status = Column(String(50))  # e.g., "completed", "failed", "pending"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")

class CreditInquiry(Base):
    __tablename__ = "credit_inquiries"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    inquiry_date = Column(DateTime)
    inquiry_type = Column(String(50))  # e.g., "credit_card", "loan"
    status = Column(String(50))  # e.g., "approved", "rejected", "pending"
    
    # Relationships
    user = relationship("User", back_populates="credit_inquiries")

class RiskAnalysis(Base):
    __tablename__ = "risk_analyses"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    risk_score = Column(Float)
    risk_level = Column(String(20))  # e.g., "low", "medium", "high"
    analysis_date = Column(DateTime, default=datetime.utcnow)
    metrics = Column(JSON)  # Store additional risk metrics as JSON
    
    # Relationships
    user = relationship("User", back_populates="risk_analyses")

class SqlType(enum.Enum):
    SIMPLE_QUERY = "SIMPLE_QUERY"
    POST_PROCESS_REQUIRED_QUERY = "POST_PROCESS_REQUIRED_QUERY"
    COMPLEX_QUERY = "COMPLEX_QUERY"

class FeatureType(enum.Enum):
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    DATE = "DATE"
    SQL_FIELD = "SQL_FIELD"

# Association table for feature-tag many-to-many relationship
feature_tags = Table(
    'feature_tags',
    Base.metadata,
    Column('feature_id', Integer, ForeignKey('features.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

class SqlSet(Base):
    """SQLAlchemy model for SQL sets."""
    __tablename__ = "sql_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sql_statements = relationship("SqlStatement", back_populates="sql_set", cascade="all, delete-orphan")
    features = relationship("Feature", back_populates="sql_set")

class SqlStatement(Base):
    """SQLAlchemy model for SQL statements."""
    __tablename__ = "sql_statements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    statement = Column(String(5000), nullable=False)
    sql_type = Column(Enum(SqlType), nullable=False)
    sql_set_id = Column(Integer, ForeignKey('sql_sets.id', ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)  # Store parsed SQL metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sql_set = relationship("SqlSet", back_populates="sql_statements")
    features = relationship("Feature", back_populates="sql_statement")

class Feature(Base):
    """SQLAlchemy model for features."""
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    data_type = Column(String(20), nullable=False)
    constraints = Column(JSON)
    is_active = Column(Boolean, default=True)
    importance_score = Column(Float)
    category = Column(String(50), index=True)
    computation_logic = Column(String(1000))  # Store feature computation logic
    feature_type = Column(Enum(FeatureType), nullable=False)
    sql_set_id = Column(Integer, ForeignKey('sql_sets.id'), nullable=True)
    sql_statement_id = Column(Integer, ForeignKey('sql_statements.id'), nullable=True)
    field_name = Column(String(100))  # For SQL field features
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tags = relationship("Tag", secondary=feature_tags, back_populates="features")
    feature_values = relationship("FeatureValue", back_populates="feature", cascade="all, delete-orphan")
    sql_set = relationship("SqlSet", back_populates="features")
    sql_statement = relationship("SqlStatement", back_populates="features")
    risk_factors = relationship("RiskFactor", back_populates="feature")

    def __repr__(self):
        return f"<Feature(id={self.id}, name='{self.name}', data_type='{self.data_type}')>"

class Tag(Base):
    """SQLAlchemy model for feature tags."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    features = relationship("Feature", secondary=feature_tags, back_populates="tags")

class FeatureValue(Base):
    """SQLAlchemy model for feature values."""
    __tablename__ = "feature_values"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey('features.id', ondelete='CASCADE'), nullable=False)
    entity_id = Column(Integer, nullable=False, index=True)  # ID of the entity this value belongs to
    value = Column(JSON, nullable=False)  # Store value as JSON to handle different data types
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    feature = relationship("Feature", back_populates="feature_values")

    __table_args__ = (
        Index('idx_feature_entity', 'feature_id', 'entity_id'),  # Composite index for faster lookups
    )

class RiskFactor(Base):
    """Risk factor model for storing risk assessment rules."""
    
    __tablename__ = "risk_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"))
    weight = Column(Float)
    threshold = Column(Float)
    operator = Column(String)  # gt, lt, eq, etc.
    risk_level = Column(String)  # high, medium, low
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feature = relationship("Feature", back_populates="risk_factors")

class RiskAssessment(Base):
    """Risk assessment model for storing assessment results."""
    
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    risk_score = Column(Float)
    risk_level = Column(String)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    factors = Column(JSON)  # Store contributing risk factors
    metadata = Column(JSON)  # Store additional assessment metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "assessment_date": self.assessment_date.isoformat(),
            "factors": self.factors,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

class ModelAdjustment(Base):
    __tablename__ = "model_adjustments"
    
    id = Column(String(36), primary_key=True)
    adjustment_type = Column(String(50))  # e.g., "cutoff", "weights"
    previous_value = Column(JSON)
    new_value = Column(JSON)
    rationale = Column(String(1000))
    expected_impact = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))  # User who made the adjustment
    status = Column(String(50), default="pending")  # e.g., "pending", "approved", "rejected"

class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(String(36), primary_key=True)
    metric_name = Column(String(100))
    metric_value = Column(Float)
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    period = Column(String(50))  # e.g., "daily", "weekly", "monthly"
    metadata = Column(JSON)  # Additional metric metadata 