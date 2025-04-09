from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API URL from environment or use default
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend-python:8000")

class ActionAnalyzeUserRisk(Action):
    def name(self) -> Text:
        return "action_analyze_user_risk"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_id = tracker.get_slot("user_id")
        date_range = tracker.get_slot("date_range")
        
        if not user_id:
            dispatcher.utter_message(text="I need a user ID to analyze risk. Could you provide one?")
            return []
        
        try:
            # Default to 30d if no date range specified
            period = "30d"
            if date_range:
                # Map common date range expressions to API parameters
                date_mapping = {
                    "last month": "30d",
                    "this month": "30d",
                    "past quarter": "90d",
                    "last quarter": "90d",
                    "q1": "90d",
                    "q2": "90d", 
                    "q3": "90d",
                    "q4": "90d",
                    "past week": "7d",
                    "last week": "7d",
                    "this year": "1y",
                    "last year": "1y",
                    "2023": "1y"
                }
                period = date_mapping.get(date_range.lower(), "30d")
            
            # Make request to backend API
            url = f"{BACKEND_API_URL}/api/risk-analysis/{user_id}?period={period}"
            logger.info(f"Making request to: {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            risk_score = data.get("risk_score", 0)
            risk_level = data.get("risk_level", "unknown").upper()
            
            # Format a nice response
            message = (
                f"Risk analysis for user {user_id}:\n"
                f"- Risk Score: {risk_score:.1f}\n"
                f"- Risk Level: {risk_level}\n"
                f"- Transactions: {data.get('transactions_summary', {}).get('count', 0)}\n"
                f"- Credit Inquiries: {data.get('credit_inquiries_summary', {}).get('count', 0)}"
            )
            
            dispatcher.utter_message(text=message)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            dispatcher.utter_message(text=f"I couldn't retrieve risk data for user {user_id}. The service might be unavailable.")
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while analyzing risk data.")
            
        return []

class ActionGetModelPerformance(Action):
    def name(self) -> Text:
        return "action_get_model_performance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Make request to backend API
            response = requests.get(f"{BACKEND_API_URL}/api/model/metrics")
            response.raise_for_status()
            
            data = response.json()
            
            # Extract metrics
            current_metrics = data.get("current", {})
            historical_metrics = data.get("historical", [])
            
            # Format a nice response
            message = (
                f"Current model performance:\n"
                f"- AUC Score: {current_metrics.get('auc', 0):.3f}\n"
                f"- Accuracy: {current_metrics.get('accuracy', 0):.3f}\n"
                f"- Precision: {current_metrics.get('precision', 0):.3f}\n"
                f"- Recall: {current_metrics.get('recall', 0):.3f}\n\n"
                f"The model performance has "
            )
            
            # Add trend information if historical data exists
            if historical_metrics and len(historical_metrics) > 1:
                current = historical_metrics[-1].get("value", 0)
                previous = historical_metrics[-2].get("value", 0)
                
                if current > previous:
                    message += f"improved by {((current - previous) / previous * 100):.1f}% since the last evaluation."
                elif current < previous:
                    message += f"decreased by {((previous - current) / previous * 100):.1f}% since the last evaluation."
                else:
                    message += "remained stable since the last evaluation."
            else:
                message += "no historical comparison available at this time."
            
            dispatcher.utter_message(text=message)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            dispatcher.utter_message(text="I couldn't retrieve model performance metrics. The service might be unavailable.")
        except Exception as e:
            logger.error(f"Error in getting model performance: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while retrieving model performance data.")
            
        return []

class ActionExplainRiskScore(Action):
    def name(self) -> Text:
        return "action_explain_risk_score"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_id = tracker.get_slot("user_id")
        risk_level = tracker.get_slot("risk_level")
        
        # Explanation without specific user data
        general_explanation = (
            "The risk score is calculated based on several factors including:\n"
            "1. Payment history (35%)\n"
            "2. Credit utilization (30%)\n"
            "3. Length of credit history (15%)\n"
            "4. Recent credit inquiries (10%)\n"
            "5. Types of credit accounts (10%)\n\n"
            "Scores typically range from 300-850, with higher scores indicating lower risk."
        )
        
        # If we have user ID, get specific data
        if user_id:
            try:
                response = requests.get(f"{BACKEND_API_URL}/api/risk-analysis/{user_id}/factors")
                
                if response.status_code == 200:
                    data = response.json()
                    factors = data.get("risk_factors", [])
                    
                    if factors:
                        message = f"For user {user_id}, the main risk factors are:\n"
                        for factor in factors:
                            message += f"- {factor['name']}: {factor['contribution']:.1f}%\n"
                        message += "\n" + general_explanation
                        
                        dispatcher.utter_message(text=message)
                        return []
            
            except Exception as e:
                logger.error(f"Error in explaining risk score: {str(e)}")
        
        # Risk level specific explanation
        if risk_level:
            level_explanation = ""
            if risk_level.lower() == "high":
                level_explanation = (
                    "High risk classifications typically result from multiple negative factors such as:\n"
                    "- Missed payments\n"
                    "- High credit utilization\n"
                    "- Numerous recent credit applications\n"
                    "- Short credit history\n\n"
                )
            elif risk_level.lower() == "medium":
                level_explanation = (
                    "Medium risk classifications usually indicate:\n"
                    "- Generally good credit behavior with some concerns\n"
                    "- Occasional late payments\n"
                    "- Moderate credit utilization\n"
                    "- Some recent credit applications\n\n"
                )
            elif risk_level.lower() == "low":
                level_explanation = (
                    "Low risk classifications indicate:\n"
                    "- Consistent on-time payments\n"
                    "- Low credit utilization\n"
                    "- Established credit history\n"
                    "- Few recent credit applications\n\n"
                )
                
            dispatcher.utter_message(text=level_explanation + general_explanation)
            return []
        
        # Default explanation
        dispatcher.utter_message(text=general_explanation)
        return []

class ActionGetFeatureImportance(Action):
    def name(self) -> Text:
        return "action_get_feature_importance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        feature_name = tracker.get_slot("feature_name")
        
        try:
            # Make request to backend API
            response = requests.get(f"{BACKEND_API_URL}/api/features/importance")
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            # If specific feature requested
            if feature_name:
                for feature in features:
                    if feature_name.lower() in feature.get("name", "").lower():
                        message = (
                            f"Feature: {feature.get('name')}\n"
                            f"- Importance: {feature.get('importance', 0):.2f}\n"
                            f"- Rank: {feature.get('rank', 'N/A')} out of {len(features)}\n"
                            f"- Description: {feature.get('description', 'No description available')}"
                        )
                        dispatcher.utter_message(text=message)
                        return []
                
                dispatcher.utter_message(text=f"I couldn't find information about the '{feature_name}' feature.")
                return []
            
            # Sort features by importance
            sorted_features = sorted(features, key=lambda x: x.get("importance", 0), reverse=True)
            top_features = sorted_features[:5]  # Get top 5
            
            message = "Top 5 most important features for risk assessment:\n"
            for i, feature in enumerate(top_features, 1):
                message += f"{i}. {feature.get('name')} - {feature.get('importance', 0):.2f}\n"
            
            dispatcher.utter_message(text=message)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            dispatcher.utter_message(text="I couldn't retrieve feature importance data. The service might be unavailable.")
        except Exception as e:
            logger.error(f"Error in getting feature importance: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while retrieving feature importance data.")
            
        return []

class ActionAdjustModelParameters(Action):
    def name(self) -> Text:
        return "action_adjust_model_parameters"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        model_parameter = tracker.get_slot("model_parameter")
        cutoff_value = tracker.get_slot("cutoff_value")
        
        # Default text when no specific parameter is mentioned
        if not model_parameter:
            message = (
                "I can help you adjust model parameters like the risk cutoff threshold. "
                "You can specify a parameter name and value, for example: "
                "'set cutoff to 0.75' or 'adjust threshold to 0.8'."
            )
            dispatcher.utter_message(text=message)
            return []
        
        # Handle cutoff adjustment
        if cutoff_value and (model_parameter.lower() in ["cutoff", "threshold", "sensitivity"]):
            try:
                # Convert string to float
                cutoff_float = float(cutoff_value)
                
                # Validate range
                if not (0 <= cutoff_float <= 1):
                    dispatcher.utter_message(text="The cutoff value must be between 0 and 1.")
                    return []
                
                # Make API request to adjust cutoff
                response = requests.post(
                    f"{BACKEND_API_URL}/api/model/adjustments",
                    json={
                        "type": "cutoff",
                        "new_value": {"cutoff": cutoff_float},
                        "rationale": "Adjusted via conversational interface",
                        "created_by": "chatbot"
                    }
                )
                response.raise_for_status()
                
                # Get current model metrics
                metrics_response = requests.get(f"{BACKEND_API_URL}/api/model/metrics")
                metrics_response.raise_for_status()
                metrics_data = metrics_response.json()
                
                message = (
                    f"I've successfully adjusted the model cutoff to {cutoff_float}.\n"
                    f"The updated model performance is:\n"
                    f"- AUC: {metrics_data.get('current', {}).get('auc', 0):.3f}\n"
                    f"- Precision: {metrics_data.get('current', {}).get('precision', 0):.3f}\n"
                    f"- Recall: {metrics_data.get('current', {}).get('recall', 0):.3f}"
                )
                
                dispatcher.utter_message(text=message)
                
            except ValueError:
                dispatcher.utter_message(text=f"Invalid cutoff value: {cutoff_value}. Please provide a number between 0 and 1.")
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                dispatcher.utter_message(text="I couldn't adjust the model parameters. The service might be unavailable.")
            except Exception as e:
                logger.error(f"Error in adjusting model parameters: {str(e)}")
                dispatcher.utter_message(text="Sorry, I encountered an error while adjusting model parameters.")
                
            return []
        
        # Default response for other parameters
        dispatcher.utter_message(
            text=f"The {model_parameter} parameter requires more specific configuration. "
            "Please use the web interface for advanced model adjustments."
        )
        
        return []

class ActionExplainModelDecision(Action):
    def name(self) -> Text:
        return "action_explain_model_decision"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_id = tracker.get_slot("user_id")
        
        if not user_id:
            dispatcher.utter_message(
                text="I need a user ID to explain a specific model decision. "
                "Could you provide one like 'explain decision for user 12345'?"
            )
            return []
        
        try:
            # Make request to backend API
            response = requests.get(f"{BACKEND_API_URL}/api/risk-analysis/{user_id}/decision")
            response.raise_for_status()
            
            data = response.json()
            
            decision = data.get("decision", "unknown")
            risk_score = data.get("risk_score", 0)
            threshold = data.get("threshold", 0)
            factors = data.get("key_factors", [])
            
            # Format message
            message = f"Decision explanation for user {user_id}:\n"
            
            if decision.lower() == "approved":
                message += f"The user was APPROVED with a risk score of {risk_score:.2f} (threshold: {threshold:.2f}).\n\n"
            elif decision.lower() == "rejected":
                message += f"The user was REJECTED with a risk score of {risk_score:.2f} (threshold: {threshold:.2f}).\n\n"
            else:
                message += f"The decision was {decision.upper()} with a risk score of {risk_score:.2f}.\n\n"
            
            # Add key factors
            message += "Key factors influencing this decision:\n"
            for factor in factors:
                message += f"- {factor.get('name')}: {factor.get('impact')}\n"
            
            dispatcher.utter_message(text=message)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            dispatcher.utter_message(text=f"I couldn't retrieve decision data for user {user_id}. The service might be unavailable.")
        except Exception as e:
            logger.error(f"Error in explaining model decision: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while explaining the model decision.")
            
        return []

class ActionGetApprovalRate(Action):
    def name(self) -> Text:
        return "action_get_approval_rate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        risk_level = tracker.get_slot("risk_level")
        date_range = tracker.get_slot("date_range")
        
        # Default to 30d if no date range specified
        period = "30d"
        if date_range:
            # Map common date range expressions to API parameters
            date_mapping = {
                "last month": "30d",
                "this month": "30d",
                "past quarter": "90d",
                "last quarter": "90d",
                "q1": "90d",
                "q2": "90d", 
                "q3": "90d",
                "q4": "90d",
                "past week": "7d",
                "last week": "7d",
                "this year": "1y",
                "last year": "1y",
                "2023": "1y"
            }
            period = date_mapping.get(date_range.lower(), "30d")
        
        try:
            # Construct URL with query parameters
            url = f"{BACKEND_API_URL}/api/metrics/approval-rate?period={period}"
            
            if risk_level:
                url += f"&risk_level={risk_level.lower()}"
            
            # Make request to backend API
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            overall_rate = data.get("overall_approval_rate", 0) * 100
            by_risk_level = data.get("by_risk_level", {})
            
            # Format message
            period_text = "the past 30 days"
            if period == "7d":
                period_text = "the past week"
            elif period == "90d":
                period_text = "the past quarter"
            elif period == "1y":
                period_text = "the past year"
            
            if risk_level:
                specific_rate = by_risk_level.get(risk_level.lower(), 0) * 100
                message = f"For {risk_level.upper()} risk users during {period_text}, the approval rate is {specific_rate:.1f}%."
            else:
                message = f"Overall approval rate for {period_text}: {overall_rate:.1f}%\n\n"
                message += "Approval rates by risk level:\n"
                
                for level, rate in by_risk_level.items():
                    message += f"- {level.upper()}: {rate * 100:.1f}%\n"
            
            dispatcher.utter_message(text=message)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            dispatcher.utter_message(text="I couldn't retrieve approval rate data. The service might be unavailable.")
        except Exception as e:
            logger.error(f"Error in getting approval rate: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while retrieving approval rate data.")
            
        return [] 