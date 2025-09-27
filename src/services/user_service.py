"""
User management service for Flowzmith.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import secrets
import hashlib

from ..models import (
    User,
    UserDataControl,
    PersonaType,
    DataRetentionPreference
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management and authentication."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()

    def create_user(
        self,
        email: str,
        password: str,
        persona_type: PersonaType,
        full_name: Optional[str] = None,
        organization: Optional[str] = None
    ) -> User:
        """Create a new user account."""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")

            # Hash password
            password_hash = self._hash_password(password)

            # Create user
            user = User(
                email=email,
                password_hash=password_hash,
                persona_type=persona_type,
                full_name=full_name,
                organization=organization,
                is_active=True
            )

            self.db_session.add(user)
            self.db_session.commit()

            # Create default data control settings
            self._create_default_data_control(user)

            logger.info(f"Created new user: {email} with persona {persona_type}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None

            if not user.is_active:
                logger.warning(f"Authentication attempt for inactive user: {email}")
                return None

            if self._verify_password(password, user.password_hash):
                # Update last login
                user.last_login = datetime.utcnow()
                self.db_session.commit()

                logger.info(f"User authenticated successfully: {email}")
                return user
            else:
                logger.warning(f"Failed authentication attempt for: {email}")
                return None

        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db_session.query(User).filter(
            User.email == email.lower()
        ).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db_session.query(User).filter(
            User.id == user_id
        ).first()

    def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> User:
        """Update user profile information."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Update allowed fields
            allowed_fields = ['full_name', 'organization', 'persona_type']
            for field in allowed_fields:
                if field in updates:
                    setattr(user, field, updates[field])

            self.db_session.commit()

            logger.info(f"Updated profile for user {user_id}")
            return user

        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {e}")
            raise

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                raise ValueError("Invalid current password")

            # Update password
            user.password_hash = self._hash_password(new_password)
            self.db_session.commit()

            logger.info(f"Password changed for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to change password for user {user_id}: {e}")
            raise

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            user.is_active = False
            self.db_session.commit()

            logger.info(f"Deactivated user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise

    def activate_user(self, user_id: str) -> bool:
        """Activate user account."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            user.is_active = True
            self.db_session.commit()

            logger.info(f"Activated user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to activate user {user_id}: {e}")
            raise

    def get_users_by_persona(self, persona_type: PersonaType) -> List[User]:
        """Get all users with a specific persona."""
        return self.db_session.query(User).filter(
            User.persona_type == persona_type,
            User.is_active == True
        ).all()

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

            # Update allowed fields
            allowed_fields = [
                'data_retention_period',
                'allow_learning_data_usage',
                'allow_analytics_sharing',
                'marketing_consent',
                'export_format_preference'
            ]

            for field in allowed_fields:
                if field in settings:
                    setattr(data_control, field, settings[field])

            self.db_session.commit()

            logger.info(f"Updated data control settings for user {user_id}")
            return data_control

        except Exception as e:
            logger.error(f"Failed to update data control settings for user {user_id}: {e}")
            raise

    def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user activity summary."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Count contract submissions
            from ..models import ContractSubmission
            submission_count = self.db_session.query(ContractSubmission).filter(
                ContractSubmission.user_id == user_id
            ).count()

            # Count successful deployments
            from ..models import DeploymentLog
            successful_deployments = self.db_session.query(DeploymentLog).join(
                ContractSubmission
            ).filter(
                ContractSubmission.user_id == user_id,
                DeploymentLog.status == 'SUCCESS'
            ).count()

            # Calculate success rate
            total_deployments = self.db_session.query(DeploymentLog).join(
                ContractSubmission
            ).filter(
                ContractSubmission.user_id == user_id
            ).count()

            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0

            return {
                "user_id": user_id,
                "email": user.email,
                "persona_type": user.persona_type.value,
                "full_name": user.full_name,
                "organization": user.organization,
                "member_since": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "total_submissions": submission_count,
                "successful_deployments": successful_deployments,
                "total_deployments": total_deployments,
                "success_rate": round(success_rate, 2),
                "is_active": user.is_active
            }

        except Exception as e:
            logger.error(f"Failed to get activity summary for user {user_id}: {e}")
            return {}

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get overall user statistics."""
        try:
            total_users = self.db_session.query(User).count()
            active_users = self.db_session.query(User).filter(
                User.is_active == True
            ).count()

            # Users by persona
            persona_stats = {}
            for persona_type in PersonaType:
                count = self.db_session.query(User).filter(
                    User.persona_type == persona_type,
                    User.is_active == True
                ).count()
                persona_stats[persona_type.value] = count

            # Recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = self.db_session.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()

            # Active users (last 30 days)
            active_recently = self.db_session.query(User).filter(
                User.last_login >= thirty_days_ago,
                User.is_active == True
            ).count()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "persona_distribution": persona_stats,
                "recent_registrations_30d": recent_registrations,
                "active_users_30d": active_recently,
                "activation_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
            }

        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {}

    def request_account_deletion(self, user_id: str) -> str:
        """Request account deletion with confirmation token."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Generate deletion token
            deletion_token = secrets.token_urlsafe(32)
            user.deletion_token = deletion_token
            user.deletion_requested_at = datetime.utcnow()

            self.db_session.commit()

            logger.info(f"Account deletion requested for user {user_id}")
            return deletion_token

        except Exception as e:
            logger.error(f"Failed to request account deletion for user {user_id}: {e}")
            raise

    def confirm_account_deletion(self, user_id: str, deletion_token: str) -> bool:
        """Confirm account deletion with token."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Validate token
            if (user.deletion_token != deletion_token or
                not user.deletion_requested_at or
                datetime.utcnow() - user.deletion_requested_at > timedelta(hours=24)):
                raise ValueError("Invalid or expired deletion token")

            # Mark for deletion (anonymize data)
            user.email = f"deleted_{user_id}@deleted.com"
            user.password_hash = ""
            user.full_name = "Deleted User"
            user.organization = ""
            user.is_active = False
            user.deletion_token = None
            user.deletion_requested_at = None

            self.db_session.commit()

            logger.info(f"Account deleted for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to confirm account deletion for user {user_id}: {e}")
            raise

    def _create_default_data_control(self, user: User):
        """Create default data control settings for a new user."""
        data_control = UserDataControl(
            user_id=user.id,
            data_retention_period=DataRetentionPeriod.ONE_YEAR,
            allow_learning_data_usage=True,
            allow_analytics_sharing=False,
            marketing_consent=False,
            export_format_preference="JSON"
        )

        self.db_session.add(data_control)

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt or fallback."""
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except ImportError:
            # Fallback to SHA-256 (less secure)
            return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except ImportError:
            # Fallback to SHA-256
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == password_hash

    def cleanup_inactive_users(self, days_inactive: int = 365) -> int:
        """Clean up users inactive for specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

            inactive_users = self.db_session.query(User).filter(
                User.is_active == True,
                or_(
                    User.last_login < cutoff_date,
                    and_(
                        User.last_login.is_(None),
                        User.created_at < cutoff_date
                    )
                )
            ).all()

            count = len(inactive_users)
            for user in inactive_users:
                user.is_active = False

            self.db_session.commit()

            logger.info(f"Deactivated {count} inactive users")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup inactive users: {e}")
            return 0