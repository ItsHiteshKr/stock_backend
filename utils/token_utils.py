from fastapi import logger,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,HTTPBearer
from fastapi_mail import ConnectionConfig
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import EmailStr
import  redis
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# Initialize password context
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()  

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

ACCESS_TOKEN_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS").lower() == "true"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS").lower() == "true"


if not all([MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM]):
    raise ValueError("Email configuration is incomplete. Please check your .env file.")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def get_refresh_token(email: EmailStr):
    """Get refresh token from Redis"""
    try:
        return redis_client.get(f"refresh_token:{email}")
    except Exception as e:
        print(f"Redis error: {e}")
        return None


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=JWT_ALGORITHM)


def is_refresh_token_valid(email: EmailStr, refresh_token: str) -> bool:
    stored_token = get_refresh_token(email)
    return stored_token == refresh_token

    
def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
    

def store_refresh_token(email: EmailStr, refresh_token: str):
    """Store refresh token in Redis with expiry"""
    try:
        # Set token with expiry time
        expire_days = REFRESH_TOKEN_EXPIRE_DAYS
        redis_client.setex(
            name=f"refresh_token:{email}",
            time=timedelta(days=expire_days),
            value=refresh_token
        )
        return True
    except Exception as e:
        print(f"Redis error: {e}")
        return False
    

def create_reset_token(email: EmailStr) -> str:
    """Create JWT token for password reset"""
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRY_MINUTES),
        'iat': datetime.utcnow(),
        'purpose': 'password_reset'
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_reset_token(token: str) -> str:
    """Verify JWT token and return email"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get('email')
        purpose = payload.get('purpose')
        
        if not email or purpose != 'password_reset':
            logger.warning("Invalid JWT  token payload")
            return None
        return email
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None

def blacklist_access_token(token: str):
    """Blacklist an access token in Redis"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp = payload.get('exp')
        if exp:
            # Calculate TTL (time to live) until token expires
            ttl = exp - int(datetime.utcnow().timestamp())
            if ttl > 0:
                redis_client.setex(f"blacklist:{token}", ttl, "true")
                return True
    except Exception as e:
        print(f"Error blacklisting token: {e}")
    return False

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return redis_client.exists(f"blacklist:{token}") > 0
