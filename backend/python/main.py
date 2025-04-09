from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import logging
import time
from datetime import datetime
import requests
import os

from .database import get_db, engine
from .models import Base
from .config import settings
from .services import risk_service, feature_service, model_service
from .services.feature_service import FeatureService
from .services.risk_service import RiskService
from .routers import feature, sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Credit Risk AI Assistant API",
    description="API for credit risk analysis and model management",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feature.router)
app.include_router(sql.router)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Rasa server URL
RASA_SERVER_URL = os.getenv("RASA_SERVER_URL", "http://rasa:5005")

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Implement rate limiting logic here
    # This is a simple example - you should implement proper rate limiting
    
    response = await call_next(request)
    return response

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Chatbot endpoints
@app.post("/api/chat/message")
async def send_message(request_data: Dict[str, Any]):
    """
    Handle chat messages and return responses
    """
    try:
        # Extract message from request
        message = request_data.get("message", "")
        sender_id = request_data.get("sender_id", "default_user")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Simple response logic
        response_text = "I'm sorry, I'm having trouble understanding that right now. Could you try rephrasing your question?"
        
        # Basic keyword matching
        message_lower = message.lower()
        if "performance" in message_lower:
            response_text = "Our current model performance metrics show an accuracy of 82% and a precision of 80%."
        elif "risk" in message_lower and "user" in message_lower:
            response_text = "To analyze risk for a specific user, please provide their user ID."
        elif "approval rate" in message_lower:
            response_text = "The current approval rate for all customers is 75%."
        elif "risk scores" in message_lower or "calculate" in message_lower:
            response_text = "Risk scores are calculated based on multiple factors including credit history, income, and transaction patterns."
        elif "features" in message_lower and "important" in message_lower:
            response_text = "The most important features for risk assessment are credit history, income level, and payment behavior."
        elif "rejected" in message_lower:
            response_text = "To understand why a user was rejected, please provide their user ID for detailed analysis."
        elif "cutoff" in message_lower:
            response_text = "The current risk cutoff threshold is 0.75. You can adjust this in the Model Adjustments section."
        
        return {"responses": [{"text": response_text}]}
    
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return {"responses": [{"text": "An error occurred while processing your message. Please try again."}]}

@app.get("/api/chat/health")
async def check_chatbot_health():
    """
    Check if the Rasa chatbot is healthy and responsive
    """
    try:
        response = requests.get(f"{RASA_SERVER_URL}/status")
        
        if response.ok:
            return {
                "status": "healthy",
                "rasa_status": response.json(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "detail": "Rasa server returned an error",
                "timestamp": datetime.utcnow().isoformat()
            }
    except requests.RequestException as e:
        logger.error(f"Error connecting to Rasa: {e}")
        return {
            "status": "unhealthy",
            "detail": "Could not connect to Rasa server",
            "timestamp": datetime.utcnow().isoformat()
        }

# Risk Analysis endpoints
@app.get("/api/risk-analysis/{user_id}")
async def get_risk_analysis(
    user_id: str,
    period: str = "30d",
    db: Session = Depends(get_db)
):
    try:
        return await risk_service.analyze_user_risk(user_id, period, db)
    except Exception as e:
        logger.error(f"Error analyzing risk for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-analysis/{user_id}/summary")
async def get_risk_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        return await risk_service.get_risk_summary(user_id, db)
    except Exception as e:
        logger.error(f"Error getting risk summary for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-analysis/{user_id}/transactions")
async def get_user_transactions(
    user_id: str,
    period: str = "30d",
    db: Session = Depends(get_db)
):
    try:
        return await risk_service.get_user_transactions(user_id, period, db)
    except Exception as e:
        logger.error(f"Error getting transactions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-analysis/{user_id}/factors")
async def get_risk_factors(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        return {"risk_factors": await risk_service.get_risk_factors(user_id, db)}
    except Exception as e:
        logger.error(f"Error getting risk factors for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-analysis/{user_id}/decision")
async def get_decision_explanation(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        return await risk_service.get_decision_explanation(user_id, db)
    except Exception as e:
        logger.error(f"Error getting decision explanation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Feature Management endpoints
@app.get("/api/features")
async def get_features(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get paginated list of features.
    """
    try:
        feature_service = FeatureService(db)
        return await feature_service.get_features(page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/features")
async def create_feature(
    feature_data: Dict,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Create a new feature.
    """
    try:
        feature_service = FeatureService(db)
        return await feature_service.create_feature(feature_data)
    except Exception as e:
        logger.error(f"Error creating feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/features")
async def update_feature(
    feature_data: Dict,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Update an existing feature.
    """
    try:
        feature_service = FeatureService(db)
        return await feature_service.update_feature(feature_data)
    except Exception as e:
        logger.error(f"Error updating feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features/importance")
async def get_feature_importance(
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get feature importance information.
    """
    try:
        feature_service = FeatureService(db)
        return await feature_service.get_feature_importance()
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model Management endpoints
@app.get("/api/model/metrics")
async def get_model_metrics(
    db: Session = Depends(get_db)
):
    try:
        return await model_service.get_model_metrics(db)
    except Exception as e:
        logger.error(f"Error fetching model metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model/cutoff")
async def get_model_cutoff(
    db: Session = Depends(get_db)
):
    try:
        return {"cutoff": await model_service.get_model_cutoff(db)}
    except Exception as e:
        logger.error(f"Error fetching model cutoff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/model/adjustments")
async def create_model_adjustment(
    adjustment_data: dict,
    db: Session = Depends(get_db)
):
    try:
        return await model_service.record_model_adjustment(adjustment_data, db)
    except Exception as e:
        logger.error(f"Error recording model adjustment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model/adjustments")
async def get_adjustment_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        return {"adjustments": await model_service.get_adjustment_history(limit, db)}
    except Exception as e:
        logger.error(f"Error fetching adjustment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/approval-rate")
async def get_approval_rate(
    period: str = "30d",
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return await risk_service.get_approval_rate(period, risk_level, db)
    except Exception as e:
        logger.error(f"Error fetching approval rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Risk assessment endpoints
@app.post("/api/risk/assess")
async def assess_risk(
    assessment_data: Dict,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Perform risk assessment based on provided data.
    """
    try:
        risk_service = RiskService(db)
        return await risk_service.assess_risk(assessment_data)
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/factors")
async def get_risk_factors(
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get list of risk factors and their weights.
    """
    try:
        risk_service = RiskService(db)
        return await risk_service.get_risk_factors()
    except Exception as e:
        logger.error(f"Error getting risk factors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 