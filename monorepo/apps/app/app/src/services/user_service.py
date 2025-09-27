from sqlalchemy.orm import Session
from src.models.user import User, DataControl
from src.models.database import get_db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.config import settings
from typing import Optional

class UserService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS

    def create_user(self, db: Session, email: str, full_name: str, password: str, persona_type: str) -> User:
        """Create a new user"""
        user = User(
            email=email,
            full_name=full_name,
            persona_type=persona_type
        )
        user.set_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.verify_password(password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def log_data_control(self, db: Session, user_id: int, data_type: str, action: str, details: str = None):
        """Log data control actions for GDPR compliance"""
        control = DataControl(
            user_id=user_id,
            data_type=data_type,
            action=action,
            details=details
        )
        db.add(control)
        db.commit()

    def export_user_data(self, db: Session, user_id: int) -> dict:
        """Export user data for GDPR compliance"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None

        user_data = {
            "user_info": {
                "email": user.email,
                "full_name": user.full_name,
                "persona_type": user.persona_type,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active
            },
            "data_controls": [
                {
                    "data_type": dc.data_type,
                    "action": dc.action,
                    "details": dc.details,
                    "created_at": dc.created_at.isoformat()
                }
                for dc in user.data_controls
            ]
        }

        # Log the export action
        self.log_data_control(db, user_id, "USER_DATA", "EXPORT", "User requested data export")

        return user_data