from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from uuid import uuid4

from ..models import User, Transaction, CreditInquiry, RiskAnalysis
from ..config import settings

logger = logging.getLogger(__name__)

class RiskService:
    def __init__(self, db: Session):
        self.db = db

    async def analyze_user_risk(self, user_id: str, period: str = "30d") -> Dict:
        """
        Analyze risk metrics for a specific user over a given period.
        
        Args:
            user_id: The ID of the user to analyze
            period: Analysis period (e.g., "30d", "90d", "1y")
            
        Returns:
            Dict containing risk metrics and analysis
        """
        try:
            # Get user data
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Calculate period dates
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, period)

            # Get transactions
            transactions = self._get_user_transactions(user_id, start_date, end_date)
            
            # Get credit inquiries
            credit_inquiries = self._get_user_credit_inquiries(user_id, start_date, end_date)

            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(transactions, credit_inquiries)

            # Create risk analysis record
            risk_analysis = self._create_risk_analysis(user_id, risk_metrics)

            return {
                "user_id": user_id,
                "analysis_date": datetime.utcnow().isoformat(),
                "period": period,
                "risk_score": risk_metrics["risk_score"],
                "risk_level": risk_metrics["risk_level"],
                "metrics": risk_metrics,
                "transactions_summary": self._summarize_transactions(transactions),
                "credit_inquiries_summary": self._summarize_credit_inquiries(credit_inquiries)
            }

        except Exception as e:
            logger.error(f"Error analyzing risk for user {user_id}: {e}")
            raise

    async def get_risk_summary(self, user_id: str) -> Dict:
        """
        Get a summary of the user's risk profile.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dict containing risk summary
        """
        try:
            # Get latest risk analysis
            latest_analysis = (
                self.db.query(RiskAnalysis)
                .filter(RiskAnalysis.user_id == user_id)
                .order_by(RiskAnalysis.analysis_date.desc())
                .first()
            )

            if not latest_analysis:
                raise ValueError(f"No risk analysis found for user {user_id}")

            return {
                "user_id": user_id,
                "risk_score": latest_analysis.risk_score,
                "risk_level": latest_analysis.risk_level,
                "analysis_date": latest_analysis.analysis_date.isoformat(),
                "metrics": latest_analysis.metrics
            }

        except Exception as e:
            logger.error(f"Error getting risk summary for user {user_id}: {e}")
            raise

    def _calculate_start_date(self, end_date: datetime, period: str) -> datetime:
        """Calculate start date based on period string."""
        period_map = {
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365),
            "6m": timedelta(days=180)
        }
        
        if period not in period_map:
            raise ValueError(f"Invalid period: {period}")
            
        return end_date - period_map[period]

    def _get_user_transactions(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transaction]:
        """Get user transactions within date range."""
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.created_at.between(start_date, end_date)
            )
            .all()
        )

    def _get_user_credit_inquiries(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[CreditInquiry]:
        """Get user credit inquiries within date range."""
        return (
            self.db.query(CreditInquiry)
            .filter(
                CreditInquiry.user_id == user_id,
                CreditInquiry.inquiry_date.between(start_date, end_date)
            )
            .all()
        )

    def _calculate_risk_metrics(
        self,
        transactions: List[Transaction],
        credit_inquiries: List[CreditInquiry]
    ) -> Dict:
        """Calculate risk metrics from transaction and credit inquiry data."""
        # Calculate transaction metrics
        transaction_metrics = self._calculate_transaction_metrics(transactions)
        
        # Calculate credit inquiry metrics
        credit_metrics = self._calculate_credit_metrics(credit_inquiries)
        
        # Calculate overall risk score (example implementation)
        risk_score = self._calculate_risk_score(transaction_metrics, credit_metrics)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "transaction_metrics": transaction_metrics,
            "credit_metrics": credit_metrics
        }

    def _calculate_transaction_metrics(self, transactions: List[Transaction]) -> Dict:
        """Calculate metrics from transaction data."""
        if not transactions:
            return {
                "total_transactions": 0,
                "total_amount": 0,
                "avg_transaction_amount": 0,
                "failed_transactions": 0,
                "success_rate": 0
            }

        total_amount = sum(t.amount for t in transactions)
        failed_transactions = sum(1 for t in transactions if t.status == "failed")
        
        return {
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "avg_transaction_amount": total_amount / len(transactions),
            "failed_transactions": failed_transactions,
            "success_rate": (len(transactions) - failed_transactions) / len(transactions)
        }

    def _calculate_credit_metrics(self, credit_inquiries: List[CreditInquiry]) -> Dict:
        """Calculate metrics from credit inquiry data."""
        if not credit_inquiries:
            return {
                "total_inquiries": 0,
                "approved_inquiries": 0,
                "rejected_inquiries": 0,
                "approval_rate": 0
            }

        approved = sum(1 for i in credit_inquiries if i.status == "approved")
        rejected = sum(1 for i in credit_inquiries if i.status == "rejected")
        
        return {
            "total_inquiries": len(credit_inquiries),
            "approved_inquiries": approved,
            "rejected_inquiries": rejected,
            "approval_rate": approved / len(credit_inquiries)
        }

    def _calculate_risk_score(
        self,
        transaction_metrics: Dict,
        credit_metrics: Dict
    ) -> float:
        """Calculate overall risk score based on metrics."""
        # This is a simplified example - implement your actual risk scoring logic
        transaction_score = (
            transaction_metrics["success_rate"] * 0.6 +
            (1 - transaction_metrics["failed_transactions"] / max(transaction_metrics["total_transactions"], 1)) * 0.4
        )
        
        credit_score = credit_metrics["approval_rate"]
        
        return (transaction_score * 0.7 + credit_score * 0.3) * 100

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on risk score."""
        if risk_score >= 80:
            return "low"
        elif risk_score >= 60:
            return "medium"
        else:
            return "high"

    def _create_risk_analysis(self, user_id: str, risk_metrics: Dict) -> RiskAnalysis:
        """Create a new risk analysis record."""
        risk_analysis = RiskAnalysis(
            id=str(uuid4()),
            user_id=user_id,
            risk_score=risk_metrics["risk_score"],
            risk_level=risk_metrics["risk_level"],
            metrics=risk_metrics
        )
        
        self.db.add(risk_analysis)
        self.db.commit()
        self.db.refresh(risk_analysis)
        
        return risk_analysis

    def _summarize_transactions(self, transactions: List[Transaction]) -> Dict:
        """Create a summary of transaction data."""
        if not transactions:
            return {
                "count": 0,
                "total_amount": 0,
                "by_type": {},
                "by_status": {}
            }

        summary = {
            "count": len(transactions),
            "total_amount": sum(t.amount for t in transactions),
            "by_type": {},
            "by_status": {}
        }

        for t in transactions:
            summary["by_type"][t.type] = summary["by_type"].get(t.type, 0) + 1
            summary["by_status"][t.status] = summary["by_status"].get(t.status, 0) + 1

        return summary

    def _summarize_credit_inquiries(self, credit_inquiries: List[CreditInquiry]) -> Dict:
        """Create a summary of credit inquiry data."""
        if not credit_inquiries:
            return {
                "count": 0,
                "by_type": {},
                "by_status": {}
            }

        summary = {
            "count": len(credit_inquiries),
            "by_type": {},
            "by_status": {}
        }

        for i in credit_inquiries:
            summary["by_type"][i.inquiry_type] = summary["by_type"].get(i.inquiry_type, 0) + 1
            summary["by_status"][i.status] = summary["by_status"].get(i.status, 0) + 1

        return summary 