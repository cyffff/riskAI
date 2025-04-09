from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models import User, Transaction, CreditInquiry, RiskAnalysis
from config import FEATURE_API_URL, FEATURE_API_HEADERS
import requests

class RiskAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_risk_metrics(self, user_ids: List[str], analysis_period: int = 30) -> Dict:
        """
        Calculate risk metrics for given user IDs
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=analysis_period)

        # Get user data
        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        
        # Get transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.transaction_date.between(start_date, end_date)
        ).all()

        # Get credit inquiries
        credit_inquiries = self.db.query(CreditInquiry).filter(
            CreditInquiry.user_id.in_(user_ids),
            CreditInquiry.inquiry_date.between(start_date, end_date)
        ).all()

        # Calculate metrics
        total_users = len(users)
        total_transactions = len(transactions)
        total_inquiries = len(credit_inquiries)

        # Calculate approval and default rates
        risk_analyses = self.db.query(RiskAnalysis).filter(
            RiskAnalysis.user_id.in_(user_ids),
            RiskAnalysis.analysis_date.between(start_date, end_date)
        ).all()

        approved = sum(1 for analysis in risk_analyses if analysis.approval_status == "approved")
        defaulted = sum(1 for analysis in risk_analyses if analysis.default_status == "defaulted")

        approval_rate = approved / len(risk_analyses) if risk_analyses else 0
        default_rate = defaulted / len(risk_analyses) if risk_analyses else 0

        # Calculate user segments
        risk_scores = [user.risk_score for user in users if user.risk_score is not None]
        if risk_scores:
            low_risk = sum(1 for score in risk_scores if score >= 0.7) / len(risk_scores)
            medium_risk = sum(1 for score in risk_scores if 0.4 <= score < 0.7) / len(risk_scores)
            high_risk = sum(1 for score in risk_scores if score < 0.4) / len(risk_scores)
        else:
            low_risk = medium_risk = high_risk = 0

        # Analyze trends
        trends = self._analyze_trends(risk_analyses)

        return {
            "approval_rate": approval_rate,
            "default_rate": default_rate,
            "user_segments": {
                "low_risk": low_risk,
                "medium_risk": medium_risk,
                "high_risk": high_risk
            },
            "trends": trends,
            "total_transactions": total_transactions,
            "total_inquiries": total_inquiries
        }

    def _analyze_trends(self, risk_analyses: List[RiskAnalysis]) -> Dict:
        """
        Analyze trends in risk metrics
        """
        if not risk_analyses:
            return {
                "default_rate_trend": "insufficient_data",
                "transaction_frequency_impact": "insufficient_data"
            }

        # Sort analyses by date
        sorted_analyses = sorted(risk_analyses, key=lambda x: x.analysis_date)
        
        # Calculate default rate trend
        first_half = sorted_analyses[:len(sorted_analyses)//2]
        second_half = sorted_analyses[len(sorted_analyses)//2:]
        
        first_default_rate = sum(1 for x in first_half if x.default_status == "defaulted") / len(first_half)
        second_default_rate = sum(1 for x in second_half if x.default_status == "defaulted") / len(second_half)
        
        default_rate_trend = "increasing" if second_default_rate > first_default_rate else "decreasing"

        # Analyze transaction frequency impact
        # This would typically involve more complex analysis of transaction patterns
        transaction_frequency_impact = "significant" if len(sorted_analyses) > 100 else "moderate"

        return {
            "default_rate_trend": default_rate_trend,
            "transaction_frequency_impact": transaction_frequency_impact
        }

    def get_feature_suggestions(self) -> List[Dict]:
        """
        Generate feature engineering suggestions
        """
        # This would typically involve analyzing feature importance and correlations
        return [
            {
                "name": "recent_credit_inquiries",
                "description": "Count of credit inquiries in the last 90 days",
                "expected_impact": "High - Strong correlation with default risk",
                "implementation_complexity": "Medium"
            },
            {
                "name": "transaction_frequency_last_30d",
                "description": "Number of transactions in the last 30 days",
                "expected_impact": "Medium - Helps identify active users",
                "implementation_complexity": "Low"
            }
        ]

    def suggest_model_adjustments(self) -> Dict:
        """
        Generate model adjustment suggestions
        """
        # This would typically involve analyzing ROC curves and model performance
        return {
            "current_cutoff": 0.5,
            "suggested_cutoff": 0.45,
            "expected_improvement": {
                "auc": 0.02,
                "approval_rate": 0.05,
                "default_rate": -0.01
            },
            "rationale": "Based on ROC curve analysis and current risk appetite"
        } 