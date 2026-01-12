from datetime import datetime, timedelta
import jose
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# Environment Variables Setup
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secretkey')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """
    Hash a password to securely manage it.
    """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """
    Verify if a plain password matches the hashed password (for security access validations).
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_tokens(data: dict):
    """
    Create an access and a refresh JWT tokens.
    Returns both of them.
    """
    
    # Access Token
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jose.jwt.encode({**data, "exp": access_expire, "type": "access"}, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = jose.jwt.encode({**data, "exp": refresh_expire, "type": "refresh"}, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token