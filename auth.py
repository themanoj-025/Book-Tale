"""
auth.py - Authentication and session management
"""

import hashlib
import os
from typing import Optional

from user import User
from config import Config
from exceptions import AuthenticationError


def hash_password(password: str) -> str:
    """SHA-256 with random salt"""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed = stored_hash.split(":")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False


class AuthManager:
    """Handles user login/logout and session state."""

    def __init__(self, storage) -> None:
        self.storage = storage
        self.current_user: Optional[User] = None

    def login(self, user_id: str, password: str) -> Optional[User]:
        users = self.storage.load_users()
        user = users.get(user_id)
        if not user:
            raise AuthenticationError()
        if not verify_password(password, user.password_hash):
            raise AuthenticationError()
        # Auto-check membership expiry
        from datetime import datetime
        from user import MEMBERSHIP_VALIDITY_DAYS
        expiry = datetime.fromisoformat(user.membership_expiry)
        if datetime.now() > expiry and user.membership_status == "Active":
            user.membership_status = "Expired"
            self.storage.save_users(users)
        self.current_user = user
        return user

    def logout(self) -> None:
        self.current_user = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def require_role(self, *roles: str) -> bool:
        if not self.current_user:
            return False
        return self.current_user.role in roles


import secrets as _secrets

def generate_reset_token(user_id: str) -> str:
    'Generate a password reset token and return it.'
    token = _secrets.token_urlsafe(32)
    if not hasattr(AuthManager, '_reset_tokens'):
        AuthManager._reset_tokens = {}
    if not hasattr(AuthManager, '_reset_token_expiry'):
        AuthManager._reset_token_expiry = {}
    from datetime import datetime, timedelta
    AuthManager._reset_tokens[token] = user_id
    AuthManager._reset_token_expiry[token] = (datetime.now() + timedelta(hours=1)).isoformat()
    return token

def verify_reset_token(token: str) -> str | None:
    'Verify a reset token and return the user_id if valid.'
    if not hasattr(AuthManager, '_reset_tokens'):
        return None
    from datetime import datetime
    user_id = AuthManager._reset_tokens.get(token)
    if not user_id:
        return None
    expiry = AuthManager._reset_token_expiry.get(token)
    if expiry and datetime.fromisoformat(expiry) < datetime.now():
        AuthManager._reset_tokens.pop(token, None)
        AuthManager._reset_token_expiry.pop(token, None)
        return None
    return user_id

def consume_reset_token(token: str) -> str | None:
    'Verify and consume a reset token.'
    uid = verify_reset_token(token)
    if uid and hasattr(AuthManager, '_reset_tokens'):
        AuthManager._reset_tokens.pop(token, None)
        AuthManager._reset_token_expiry.pop(token, None)
    return uid

def generate_verify_token(user_id: str) -> str:
    'Generate an email verification token.'
    token = _secrets.token_urlsafe(32)
    if not hasattr(AuthManager, '_verify_tokens'):
        AuthManager._verify_tokens = {}
    AuthManager._verify_tokens[token] = user_id
    return token

def verify_email_token(token: str) -> str | None:
    'Verify an email token and return the user_id if valid.'
    if not hasattr(AuthManager, '_verify_tokens'):
        return None
    return AuthManager._verify_tokens.get(token)

def consume_verify_token(token: str) -> str | None:
    'Verify and consume an email verification token.'
    uid = verify_email_token(token)
    if uid and hasattr(AuthManager, '_verify_tokens'):
        AuthManager._verify_tokens.pop(token, None)
    return uid

