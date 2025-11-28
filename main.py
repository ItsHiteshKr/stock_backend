from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import bcrypt
import uvicorn
import traceback
from pydantic import BaseModel, EmailStr
from db.batabase import get_db, init_db
from model.user_model import UserTable
from schema.user_schema import UserCreate, UserResponse
from utils import token_utils as token




from router.user_router import router as user_router
from router.nifty_router import router as nifty_router

load_dotenv()

frontend_url = os.getenv("Frontend_URL")       

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield


app = FastAPI(
    title="Nifty Stock API",
    description="API for managing Nifty stock data",
    version="1.0.0",
    lifespan=lifespan
)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, tags=["User Management"])
app.include_router(nifty_router, tags=["Nifty Stock Data"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Nifty Stock API",
        "docs": "/docs",
    }

@app.post("/create", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new User data entry"""
    existing_user = db.query(UserTable).filter(UserTable.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Your email is already registered ! You can login.")
        
        # hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
    db_user = UserTable(
        full_name=user.full_name,
        email=user.email,
        mobile_number=user.mobile_number,
        password=hashed_password.decode('utf-8'),  # Decode to string for MySQL
        country=user.country
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", status_code=status.HTTP_200_OK)
async def user_login(user: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        db_user = db.query(UserTable).filter(UserTable.email == user.email).first()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check password - encode stored password back to bytes
        if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if db_user.active != 1:
            raise HTTPException(status_code=403, detail="Account is inactive")

        user_data = {
            "email": str(user.email)
        }

        payload = {
            "email": user_data["email"]
        }

        access_token = token.create_access_token(payload)
        refresh_token = token.create_refresh_token(payload)

        token.store_refresh_token(user_data["email"], refresh_token)

        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error: {e}")

        return {
            "message": "User logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "email": user_data["email"]
            }
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route for User logout
@app.post("/logout")
async def logout(request: Request, response: Response):
    access_token = request.headers.get("Authorization")
    refresh_token = request.cookies.get("refresh_token")

    # Blacklist access token
    if access_token and access_token.startswith("Bearer "):
        token_value = access_token.split(" ")[1]
        token.blacklist_access_token(token_value)

    # Verify and delete refresh token from Redis
    if refresh_token:
        try:
            payload = token.verify_refresh_token(refresh_token)
            if payload and payload.get("email"):
                token.delete_refresh_token(payload["email"])
        except Exception as e:
            print(f"Error deleting refresh token: {e}")
    
    # Clear the refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)