"""
Data control and privacy service for Smart Contract LLM Builder.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
import csv
import io
from pathlib import Path

from ..models import (
    UserDataControl,
    DataRetentionPreference,
    User,
    ContractSubmission,
    DeploymentLog,
    LearningFeedbackLoop
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class DataControlService:
    """Service for managing user data control and privacy."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()

    def get_user_data_control(self, user_id: str) -> Optional[UserDataControl]:
        """Get user data control settings."""
        return self.db_session.query(UserDataControl).filter(
            UserDataControl.user_id == user_id
        ).first()

    def update_data_control_settings(
        self,
        user_id: str,
        settings: Dict[str, Any]
    ) -> UserDataControl:
        """Update user data control settings."""
        try:
            data_control = self.get_user_data_control(user_id)
            if not data_control:
                raise ValueError(f"Data control settings not found for user {user_id}")

            # Update settings
            for key, value in settings.items():
                if hasattr(data_control, key):
                    setattr(data_control, key, value)

            data_control.last_updated = datetime.utcnow()
            self.db_session.commit()

            logger.info(f"Updated data control settings for user {user_id}")
            return data_control

        except Exception as e:
            logger.error(f"Failed to update data control settings for user {user_id}: {e}")
            raise

    def export_user_data(
        self,
        user_id: str,
        format_type: str = "JSON"
    ) -> Dict[str, Any]:
        """Export user data in specified format."""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id
            ).first()

            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Check if user has export rights
            data_control = self.get_user_data_control(user_id)
            if not data_control:
                raise ValueError(f"No data control settings found for user {user_id}")

            # Collect user data
            user_data = self._collect_user_data(user_id)

            # Format according to preference
            if format_type.upper() == "JSON":
                return {"format": "JSON", "data": user_data}
            elif format_type.upper() == "CSV":
                csv_data = self._convert_to_csv(user_data)
                return {"format": "CSV", "data": csv_data}
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

        except Exception as e:
            logger.error(f"Failed to export user data for user {user_id}: {e}")
            raise

    def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all user data for export."""
        try:
            # Get user profile
            user = self.db_session.query(User).filter(
                User.id == user_id
            ).first()

            profile_data = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "organization": user.organization,
                "persona_type": user.persona_type.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            }

            # Get data control settings
            data_control = self.get_user_data_control(user_id)
            control_data = {
                "data_retention_period": data_control.data_retention_period.value,
                "allow_learning_data_usage": data_control.allow_learning_data_usage,
                "allow_analytics_sharing": data_control.allow_analytics_sharing,
                "marketing_consent": data_control.marketing_consent,
                "export_format_preference": data_control.export_format_preference,
                "last_updated": data_control.last_updated.isoformat()
            }

            # Get contract submissions
            submissions = self.db_session.query(ContractSubmission).filter(
                ContractSubmission.user_id == user_id
            ).all()

            submissions_data = []
            for submission in submissions:
                submission_data = {
                    "id": str(submission.id),
                    "input_type": submission.input_type.value,
                    "content": submission.content,
                    "pre_conditions": submission.pre_conditions,
                    "post_conditions": submission.post_conditions,
                    "status": submission.status.value,
                    "created_at": submission.created_at.isoformat(),
                    "processed_at": submission.processed_at.isoformat() if submission.processed_at else None
                }

                # Include generated configuration if exists
                if submission.generated_config:
                    submission_data["generated_configuration"] = {
                        "id": str(submission.generated_config.id),
                        "config_content": submission.generated_config.config_content,
                        "validation_status": submission.generated_config.validation_status.value,
                        "validation_errors": submission.generated_config.validation_errors,
                        "created_at": submission.generated_config.created_at.isoformat()
                    }

                submissions_data.append(submission_data)

            # Get deployment logs
            deployment_logs = self.db_session.query(DeploymentLog).join(
                ContractSubmission
            ).filter(
                ContractSubmission.user_id == user_id
            ).all()

            deployment_data = []
            for log in deployment_logs:
                deployment_data.append({
                    "id": str(log.id),
                    "submission_id": str(log.submission_id),
                    "network": log.network,
                    "status": log.status.value,
                    "error_message": log.error_message,
                    "error_code": log.error_code,
                    "transaction_hash": log.transaction_hash,
                    "gas_used": log.gas_used,
                    "execution_time_ms": log.execution_time_ms,
                    "log_content": log.log_content,
                    "created_at": log.created_at.isoformat()
                })

            return {
                "profile": profile_data,
                "data_control": control_data,
                "contract_submissions": submissions_data,
                "deployment_logs": deployment_data,
                "export_metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "data_version": "1.0"
                }
            }

        except Exception as e:
            logger.error(f"Failed to collect user data for user {user_id}: {e}")
            raise

    def _convert_to_csv(self, user_data: Dict[str, Any]) -> str:
        """Convert user data to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Profile data
        writer.writerow(["Profile Data"])
        writer.writerow(["Field", "Value"])
        for key, value in user_data["profile"].items():
            writer.writerow([key, value])
        writer.writerow([])

        # Contract submissions
        writer.writerow(["Contract Submissions"])
        if user_data["contract_submissions"]:
            # Get all possible keys from all submissions
            all_keys = set()
            for sub in user_data["contract_submissions"]:
                all_keys.update(sub.keys())
                if "generated_configuration" in sub:
                    all_keys.update(f"generated_config_{k}" for k in sub["generated_configuration"].keys())

            writer.writerow(list(all_keys))

            for sub in user_data["contract_submissions"]:
                row = []
                for key in all_keys:
                    if key in sub:
                        if isinstance(sub[key], dict):
                            row.append(json.dumps(sub[key]))
                        else:
                            row.append(sub[key])
                    elif key.startswith("generated_config_") and "generated_configuration" in sub:
                        config_key = key[16:]  # Remove "generated_config_" prefix
                        row.append(sub["generated_configuration"].get(config_key, ""))
                    else:
                        row.append("")
                writer.writerow(row)
        else:
            writer.writerow(["No contract submissions found"])
        writer.writerow([])

        # Deployment logs
        writer.writerow(["Deployment Logs"])
        if user_data["deployment_logs"]:
            writer.writerow([
                "id", "submission_id", "network", "status", "error_message",
                "transaction_hash", "gas_used", "execution_time_ms", "created_at"
            ])
            for log in user_data["deployment_logs"]:
                writer.writerow([
                    log["id"], log["submission_id"], log["network"], log["status"],
                    log["error_message"], log["transaction_hash"], log["gas_used"],
                    log["execution_time_ms"], log["created_at"]
                ])
        else:
            writer.writerow(["No deployment logs found"])

        return output.getvalue()

    def delete_user_data(
        self,
        user_id: str,
        data_categories: List[str] = None
    ) -> Dict[str, int]:
        """Delete user data by category."""
        try:
            if data_categories is None:
                data_categories = ["all"]

            deletion_counts = {}

            if "all" in data_categories or "profile" in data_categories:
                # Anonymize profile data
                user = self.db_session.query(User).filter(
                    User.id == user_id
                ).first()
                if user:
                    user.email = f"deleted_{user_id}@deleted.com"
                    user.full_name = "Deleted User"
                    user.organization = ""
                    deletion_counts["profile"] = 1

            if "all" in data_categories or "submissions" in data_categories:
                # Delete contract submissions and related data
                submissions = self.db_session.query(ContractSubmission).filter(
                    ContractSubmission.user_id == user_id
                ).all()
                deletion_counts["submissions"] = len(submissions)

                for submission in submissions:
                    self.db_session.delete(submission)

            if "all" in data_categories or "deployment_logs" in data_categories:
                # Delete deployment logs
                logs = self.db_session.query(DeploymentLog).join(
                    ContractSubmission
                ).filter(
                    ContractSubmission.user_id == user_id
                ).all()
                deletion_counts["deployment_logs"] = len(logs)

                for log in logs:
                    self.db_session.delete(log)

            if "all" in data_categories or "learning_data" in data_categories:
                # Delete learning feedback data
                feedback = self.db_session.query(LearningFeedbackLoop).join(
                    ContractSubmission
                ).filter(
                    ContractSubmission.user_id == user_id
                ).all()
                deletion_counts["learning_data"] = len(feedback)

                for item in feedback:
                    self.db_session.delete(item)

            self.db_session.commit()

            logger.info(f"Deleted user data for user {user_id}: {deletion_counts}")
            return deletion_counts

        except Exception as e:
            logger.error(f"Failed to delete user data for user {user_id}: {e}")
            raise

    def apply_retention_policy(self) -> Dict[str, int]:
        """Apply data retention policy across all users."""
        try:
            retention_stats = {}

            # Get all data control settings
            data_controls = self.db_session.query(UserDataControl).all()

            for control in data_controls:
                cutoff_date = self._calculate_retention_cutoff(control.data_retention_period)

                # Count and delete old contract submissions
                old_submissions = self.db_session.query(ContractSubmission).filter(
                    ContractSubmission.user_id == control.user_id,
                    ContractSubmission.created_at < cutoff_date
                ).all()

                if old_submissions:
                    for submission in old_submissions:
                        self.db_session.delete(submission)

                    if control.user_id not in retention_stats:
                        retention_stats[control.user_id] = {"submissions": 0}
                    retention_stats[control.user_id]["submissions"] += len(old_submissions)

                # Count and delete old deployment logs
                old_logs = self.db_session.query(DeploymentLog).join(
                    ContractSubmission
                ).filter(
                    ContractSubmission.user_id == control.user_id,
                    DeploymentLog.created_at < cutoff_date
                ).all()

                if old_logs:
                    for log in old_logs:
                        self.db_session.delete(log)

                    if control.user_id not in retention_stats:
                        retention_stats[control.user_id] = {"logs": 0}
                    retention_stats[control.user_id]["logs"] += len(old_logs)

            self.db_session.commit()

            logger.info(f"Applied retention policy: {retention_stats}")
            return retention_stats

        except Exception as e:
            logger.error(f"Failed to apply retention policy: {e}")
            return {}

    def _calculate_retention_cutoff(self, retention_period: DataRetentionPreference) -> datetime:
        """Calculate cutoff date based on retention period."""
        now = datetime.utcnow()

        if retention_period == DataRetentionPreference.ONE_MONTH:
            return now - timedelta(days=30)
        elif retention_period == DataRetentionPreference.THREE_MONTHS:
            return now - timedelta(days=90)
        elif retention_period == DataRetentionPreference.SIX_MONTHS:
            return now - timedelta(days=180)
        elif retention_period == DataRetentionPreference.ONE_YEAR:
            return now - timedelta(days=365)
        elif retention_period == DataRetentionPreference.TWO_YEARS:
            return now - timedelta(days=730)
        elif retention_period == DataRetentionPreference.FIVE_YEARS:
            return now - timedelta(days=1825)
        elif retention_period == DataRetentionPreference.INDEFINITE:
            # Return a very old date for indefinite retention
            return datetime(1970, 1, 1)
        else:
            # Default to one year
            return now - timedelta(days=365)

    def get_data_usage_statistics(self) -> Dict[str, Any]:
        """Get data usage statistics across all users."""
        try:
            total_users = self.db_session.query(User).count()
            active_users = self.db_session.query(User).filter(
                User.is_active == True
            ).count()

            # Data control settings distribution
            retention_distribution = {}
            for period in DataRetentionPreference:
                count = self.db_session.query(UserDataControl).filter(
                    UserDataControl.data_retention_period == period
                ).count()
                retention_distribution[period.value] = count

            # Consent statistics
            learning_consent_count = self.db_session.query(UserDataControl).filter(
                UserDataControl.allow_learning_data_usage == True
            ).count()

            analytics_consent_count = self.db_session.query(UserDataControl).filter(
                UserDataControl.allow_analytics_sharing == True
            ).count()

            marketing_consent_count = self.db_session.query(UserDataControl).filter(
                UserDataControl.marketing_consent == True
            ).count()

            # Data volume statistics
            total_submissions = self.db_session.query(ContractSubmission).count()
            total_deployments = self.db_session.query(DeploymentLog).count()
            total_feedback = self.db_session.query(LearningFeedbackLoop).count()

            return {
                "user_statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users
                },
                "retention_distribution": retention_distribution,
                "consent_statistics": {
                    "learning_data_consent": learning_consent_count,
                    "analytics_sharing_consent": analytics_consent_count,
                    "marketing_consent": marketing_consent_count
                },
                "data_volume": {
                    "total_submissions": total_submissions,
                    "total_deployments": total_deployments,
                    "total_feedback_entries": total_feedback
                }
            }

        except Exception as e:
            logger.error(f"Failed to get data usage statistics: {e}")
            return {}

    def validate_data_compliance(self, user_id: str) -> Dict[str, Any]:
        """Validate user data compliance with GDPR/regulations."""
        try:
            compliance_issues = []

            user = self.db_session.query(User).filter(
                User.id == user_id
            ).first()

            if not user:
                return {"compliant": False, "issues": ["User not found"]}

            data_control = self.get_user_data_control(user_id)
            if not data_control:
                compliance_issues.append("No data control settings found")

            # Check if user has consented to necessary data processing
            if not data_control.allow_learning_data_usage:
                compliance_issues.append("User has not consented to learning data usage")

            # Check data retention compliance
            cutoff_date = self._calculate_retention_cutoff(data_control.data_retention_period)
            old_data_count = self.db_session.query(ContractSubmission).filter(
                ContractSubmission.user_id == user_id,
                ContractSubmission.created_at < cutoff_date
            ).count()

            if old_data_count > 0:
                compliance_issues.append(f"Found {old_data_count} records exceeding retention period")

            return {
                "compliant": len(compliance_issues) == 0,
                "issues": compliance_issues,
                "user_id": user_id,
                "validation_date": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to validate data compliance for user {user_id}: {e}")
            return {"compliant": False, "issues": [str(e)]}