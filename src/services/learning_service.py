"""
Learning and feedback service for Flowzmith.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from collections import defaultdict
import json

from ..models import (
    LearningFeedbackLoop,
    PatternType,
    ContractSubmission,
    GeneratedConfiguration,
    DeploymentLog,
    DocumentationKnowledgeBase
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class LearningService:
    """Service for learning from deployment feedback and improving contract generation."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()

    def analyze_deployment_feedback(
        self,
        deployment_log: DeploymentLog
    ) -> List[LearningFeedbackLoop]:
        """Analyze deployment logs and create learning feedback entries."""
        try:
            feedback_entries = []

            # Analyze based on deployment status
            if deployment_log.status.value == "SUCCESS":
                feedback_entries.extend(self._analyze_success_patterns(deployment_log))
            else:
                feedback_entries.extend(self._analyze_error_patterns(deployment_log))

            # Analyze for optimization opportunities regardless of status
            feedback_entries.extend(self._analyze_optimization_opportunities(deployment_log))

            # Save feedback entries
            for entry in feedback_entries:
                self.db_session.add(entry)

            self.db_session.commit()

            logger.info(f"Created {len(feedback_entries)} learning feedback entries for deployment {deployment_log.id}")
            return feedback_entries

        except Exception as e:
            logger.error(f"Failed to analyze deployment feedback for {deployment_log.id}: {e}")
            return []

    def _analyze_success_patterns(self, deployment_log: DeploymentLog) -> List[LearningFeedbackLoop]:
        """Analyze successful deployment for positive patterns."""
        patterns = []

        # Extract contract code
        contract_code = deployment_log.generated_configuration.generated_contract_code

        # Analyze contract structure patterns
        structure_insights = self._analyze_contract_structure(contract_code)
        if structure_insights:
            patterns.append(LearningFeedbackLoop(
                submission_id=deployment_log.submission_id,
                log_id=deployment_log.id,
                pattern_type=PatternType.SUCCESS_PATTERN,
                insights=structure_insights,
                confidence_score=0.8
            ))

        # Analyze configuration patterns
        config_insights = self._analyze_successful_configuration(
            deployment_log.generated_configuration.config_content
        )
        if config_insights:
            patterns.append(LearningFeedbackLoop(
                submission_id=deployment_log.submission_id,
                log_id=deployment_log.id,
                pattern_type=PatternType.SUCCESS_PATTERN,
                insights=config_insights,
                confidence_score=0.7
            ))

        return patterns

    def _analyze_error_patterns(self, deployment_log: DeploymentLog) -> List[LearningFeedbackLoop]:
        """Analyze failed deployment for error patterns."""
        patterns = []

        # Parse error message
        error_analysis = self._parse_deployment_error(
            deployment_log.error_message or "",
            deployment_log.log_content
        )

        if error_analysis:
            patterns.append(LearningFeedbackLoop(
                submission_id=deployment_log.submission_id,
                log_id=deployment_log.id,
                pattern_type=PatternType.ERROR_PATTERN,
                insights=error_analysis,
                confidence_score=0.9
            ))

        # Analyze contract-specific errors
        if deployment_log.generated_configuration:
            contract_errors = self._analyze_contract_errors(
                deployment_log.generated_configuration.generated_contract_code,
                deployment_log.log_content
            )

            if contract_errors:
                patterns.append(LearningFeedbackLoop(
                    submission_id=deployment_log.submission_id,
                    log_id=deployment_log.id,
                    pattern_type=PatternType.ERROR_PATTERN,
                    insights=contract_errors,
                    confidence_score=0.8
                ))

        return patterns

    def _analyze_optimization_opportunities(self, deployment_log: DeploymentLog) -> List[LearningFeedbackLoop]:
        """Analyze deployment for optimization opportunities."""
        patterns = []

        # Analyze gas usage
        if deployment_log.gas_used:
            gas_insights = self._analyze_gas_usage(deployment_log)
            if gas_insights:
                patterns.append(LearningFeedbackLoop(
                    submission_id=deployment_log.submission_id,
                    log_id=deployment_log.id,
                    pattern_type=PatternType.OPTIMIZATION_OPPORTUNITY,
                    insights=gas_insights,
                    confidence_score=0.6
                ))

        # Analyze execution time
        if deployment_log.execution_time_ms:
            time_insights = self._analyze_execution_time(deployment_log)
            if time_insights:
                patterns.append(LearningFeedbackLoop(
                    submission_id=deployment_log.submission_id,
                    log_id=deployment_log.id,
                    pattern_type=PatternType.OPTIMIZATION_OPPORTUNITY,
                    insights=time_insights,
                    confidence_score=0.5
                ))

        return patterns

    def _analyze_contract_structure(self, contract_code: str) -> Optional[Dict[str, Any]]:
        """Analyze contract structure for successful patterns."""
        insights = {"pattern_type": "contract_structure", "elements": []}

        # Check for good practices
        if "pub contract" in contract_code:
            insights["elements"].append({"practice": "public_contract", "found": True})

        if "pub resource" in contract_code:
            insights["elements"].append({"practice": "resource_definition", "found": True})

        if "init(" in contract_code:
            insights["elements"].append({"practice": "initializer", "found": True})

        if "destroy()" in contract_code:
            insights["elements"].append({"practice": "destroy_method", "found": True})

        if "pub event" in contract_code:
            insights["elements"].append({"practice": "event_emission", "found": True})

        # Only return if we found meaningful patterns
        if insights["elements"]:
            return insights

        return None

    def _analyze_successful_configuration(self, config_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze successful configuration patterns."""
        insights = {"pattern_type": "configuration", "elements": []}

        # Check for good configuration practices
        if "contracts" in config_content and config_content["contracts"]:
            insights["elements"].append({"practice": "contract_definitions", "found": True})

        if "networks" in config_content and config_content["networks"]:
            insights["elements"].append({"practice": "network_configuration", "found": True})

        if "accounts" in config_content and config_content["accounts"]:
            insights["elements"].append({"practice": "account_configuration", "found": True})

        if "deployments" in config_content and config_content["deployments"]:
            insights["elements"].append({"practice": "deployment_configuration", "found": True})

        # Only return if we found meaningful patterns
        if insights["elements"]:
            return insights

        return None

    def _parse_deployment_error(self, error_message: str, log_content: str) -> Optional[Dict[str, Any]]:
        """Parse deployment error patterns."""
        if not error_message:
            return None

        insights = {"pattern_type": "deployment_error", "error_type": "unknown"}

        # Classify error types
        error_lower = error_message.lower()

        if "syntax error" in error_lower:
            insights["error_type"] = "syntax_error"
            insights["suggestion"] = "Check contract syntax and Cadence language rules"
        elif "configuration error" in error_lower:
            insights["error_type"] = "configuration_error"
            insights["suggestion"] = "Validate flow.json configuration"
        elif "account not found" in error_lower:
            insights["error_type"] = "account_error"
            insights["suggestion"] = "Check Flow account configuration and funding"
        elif "insufficient funds" in error_lower:
            insights["error_type"] = "funds_error"
            insights["suggestion"] = "Ensure sufficient funds in deployment account"
        elif "invalid contract" in error_lower:
            insights["error_type"] = "contract_validation_error"
            insights["suggestion"] = "Review contract code for compliance issues"
        else:
            insights["error_type"] = "unknown_error"
            insights["suggestion"] = "Review deployment logs for specific error details"

        return insights

    def _analyze_contract_errors(self, contract_code: str, log_content: str) -> Optional[Dict[str, Any]]:
        """Analyze contract-specific errors."""
        insights = {"pattern_type": "contract_error", "issues": []}

        # Look for common issues in logs
        log_lower = log_content.lower()

        if "resource cannot be copied" in log_lower:
            insights["issues"].append({
                "issue": "resource_copy_attempt",
                "description": "Attempt to copy resource detected",
                "suggestion": "Use move/borrow semantics for resources"
            })

        if "missing capability" in log_lower:
            insights["issues"].append({
                "issue": "missing_capability",
                "description": "Required capability not found",
                "suggestion": "Ensure proper capability linking"
            })

        if "type mismatch" in log_lower:
            insights["issues"].append({
                "issue": "type_mismatch",
                "description": "Type compatibility issue",
                "suggestion": "Check type annotations and conversions"
            })

        # Only return if we found issues
        if insights["issues"]:
            return insights

        return None

    def _analyze_gas_usage(self, deployment_log: DeploymentLog) -> Optional[Dict[str, Any]]:
        """Analyze gas usage patterns."""
        gas_used = deployment_log.gas_used

        # Compare with average gas usage
        avg_gas = self._get_average_gas_usage()

        insights = {
            "pattern_type": "gas_usage",
            "gas_used": gas_used,
            "average_gas": avg_gas,
            "efficiency": "normal"
        }

        if gas_used > avg_gas * 1.5:
            insights["efficiency"] = "high"
            insights["suggestion"] = "Consider optimizing contract logic to reduce gas consumption"
        elif gas_used < avg_gas * 0.5:
            insights["efficiency"] = "low"
            insights["suggestion"] = "Excellent gas efficiency"

        return insights

    def _analyze_execution_time(self, deployment_log: DeploymentLog) -> Optional[Dict[str, Any]]:
        """Analyze execution time patterns."""
        execution_time = deployment_log.execution_time_ms

        # Compare with average execution time
        avg_time = self._get_average_execution_time()

        insights = {
            "pattern_type": "execution_time",
            "execution_time_ms": execution_time,
            "average_time_ms": avg_time,
            "performance": "normal"
        }

        if execution_time > avg_time * 2:
            insights["performance"] = "slow"
            insights["suggestion"] = "Consider optimizing contract complexity"
        elif execution_time < avg_time * 0.5:
            insights["performance"] = "fast"
            insights["suggestion"] = "Excellent deployment performance"

        return insights

    def _get_average_gas_usage(self) -> int:
        """Get average gas usage across all deployments."""
        try:
            result = self.db_session.query(func.avg(DeploymentLog.gas_used)).filter(
                DeploymentLog.gas_used.isnot(None)
            ).scalar()
            return int(result) if result else 100
        except Exception:
            return 100

    def _get_average_execution_time(self) -> int:
        """Get average execution time across all deployments."""
        try:
            result = self.db_session.query(func.avg(DeploymentLog.execution_time_ms)).scalar()
            return int(result) if result else 10000
        except Exception:
            return 10000

    def get_learning_insights(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent learning insights."""
        try:
            feedback = self.db_session.query(LearningFeedbackLoop).order_by(
                LearningFeedbackLoop.created_at.desc()
            ).limit(limit).all()

            insights = []
            for entry in feedback:
                insights.append({
                    "id": str(entry.id),
                    "pattern_type": entry.pattern_type.value,
                    "confidence_score": entry.confidence_score,
                    "insights": entry.insights,
                    "created_at": entry.created_at.isoformat(),
                    "applied_to_generation": entry.applied_to_generation
                })

            return insights

        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return []

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learning patterns."""
        try:
            # Count patterns by type
            pattern_counts = {}
            for pattern_type in PatternType:
                count = self.db_session.query(LearningFeedbackLoop).filter(
                    LearningFeedbackLoop.pattern_type == pattern_type
                ).count()
                pattern_counts[pattern_type.value] = count

            # Average confidence scores by pattern type
            confidence_scores = {}
            for pattern_type in PatternType:
                avg_confidence = self.db_session.query(func.avg(LearningFeedbackLoop.confidence_score)).filter(
                    LearningFeedbackLoop.pattern_type == pattern_type
                ).scalar()
                confidence_scores[pattern_type.value] = float(avg_confidence) if avg_confidence else 0

            # Applied to generation rate
            applied_count = self.db_session.query(LearningFeedbackLoop).filter(
                LearningFeedbackLoop.applied_to_generation == True
            ).count()
            total_count = self.db_session.query(LearningFeedbackLoop).count()

            return {
                "total_patterns": total_count,
                "pattern_distribution": pattern_counts,
                "average_confidence_scores": confidence_scores,
                "application_rate": round((applied_count / total_count * 100) if total_count > 0 else 0, 2),
                "applied_patterns": applied_count
            }

        except Exception as e:
            logger.error(f"Failed to get pattern statistics: {e}")
            return {}

    def apply_learning_to_generation(self, pattern_ids: List[str]) -> int:
        """Mark learning patterns as applied to generation."""
        try:
            updated_count = 0
            for pattern_id in pattern_ids:
                pattern = self.db_session.query(LearningFeedbackLoop).filter(
                    LearningFeedbackLoop.id == pattern_id
                ).first()

                if pattern:
                    pattern.applied_to_generation = True
                    updated_count += 1

            self.db_session.commit()

            logger.info(f"Applied {updated_count} learning patterns to generation")
            return updated_count

        except Exception as e:
            logger.error(f"Failed to apply learning patterns: {e}")
            return 0

    def get_relevant_learning_for_prompt(
        self,
        prompt_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get relevant learning patterns for contract generation."""
        try:
            # Get high-confidence patterns that haven't been applied recently
            relevant_patterns = self.db_session.query(LearningFeedbackLoop).filter(
                LearningFeedbackLoop.confidence_score >= 0.7,
                LearningFeedbackLoop.applied_to_generation == False
            ).order_by(
                LearningFeedbackLoop.created_at.desc()
            ).limit(10).all()

            patterns = []
            for pattern in relevant_patterns:
                # Check if pattern is relevant to current context
                if self._is_pattern_relevant(pattern, prompt_context):
                    patterns.append({
                        "pattern_type": pattern.pattern_type.value,
                        "insights": pattern.insights,
                        "confidence_score": pattern.confidence_score
                    })

            return patterns

        except Exception as e:
            logger.error(f"Failed to get relevant learning patterns: {e}")
            return []

    def _is_pattern_relevant(self, pattern: LearningFeedbackLoop, context: Dict[str, Any]) -> bool:
        """Check if a learning pattern is relevant to the current context."""
        # Simple relevance check based on pattern type and context
        if pattern.pattern_type == PatternType.ERROR_PATTERN:
            # Error patterns are always relevant for avoiding mistakes
            return True

        if pattern.pattern_type == PatternType.SUCCESS_PATTERN:
            # Success patterns are generally relevant
            return True

        if pattern.pattern_type == PatternType.OPTIMIZATION_OPPORTUNITY:
            # Optimization patterns are relevant for improving quality
            return True

        return False

    def cleanup_old_feedback(self, days_old: int = 90) -> int:
        """Clean up old feedback entries."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            deleted_count = self.db_session.query(LearningFeedbackLoop).filter(
                LearningFeedbackLoop.created_at < cutoff_date,
                LearningFeedbackLoop.applied_to_generation == True
            ).delete()

            self.db_session.commit()

            logger.info(f"Cleaned up {deleted_count} old feedback entries")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old feedback: {e}")
            return 0