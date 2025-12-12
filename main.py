from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import bcrypt
import uvicorn
import traceback
import logging
from pydantic import BaseModel, EmailStr
from db.database import get_db, Base, engine
from model.user_model import UserTable
from schema.user_schema import UserCreate, UserResponse
from utils import token_utils as utils
from utils.token_utils import conf
from router.live_stock_router import router as live_stock_router
from router.screener_router import router as screener_router
from router.analysis_router import router as analysis_router
from router.watchlist_router import router as watchlist_router
from router.indicators_router import router as indicators_router
from router.comparison_routes import router as comparison_routes
from router.stocks_router_for_UI import router as stocks_router_for_UI
from router.index_router_for_UI import router as index_router_for_UI


logger = logging.getLogger(__name__)

from router.user_router import router as user_router
from router.nifty_router import router as nifty_router
from admin.admin_panel import admin_panel

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


app = FastAPI(
    title="Nifty Stock API",
    description="API for managing Nifty stock data",
    version="1.0.0"
)

# Create all tables on startup
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins= [frontend_url], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, tags=["User Management"])
app.include_router(nifty_router, tags=["Nifty Stock Data"])
app.include_router(live_stock_router, tags=["Live Stock Data"])
app.include_router(screener_router, tags=["Stock Screener"])
app.include_router(analysis_router, tags=["Monthly & Historical Analysis"])
app.include_router(watchlist_router, tags=["Watchlist Management"])
app.include_router(indicators_router,tags=["Technical Indicators"])
app.include_router(comparison_routes,tags=["Stock Comparison"])
app.include_router(stocks_router_for_UI, tags=["Search and list Stocks"])
app.include_router(index_router_for_UI, tags=["Search and list Indices"])



# Mount admin panel
app.mount("/admin", admin_panel)


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

        access_token = utils.create_access_token(payload)
        refresh_token = utils.create_refresh_token(payload)

        utils.store_refresh_token(user_data["email"], refresh_token)

        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        try:
            db_user.last_login = func.now()
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
        utils.blacklist_access_token(token_value)

    # Verify and delete refresh token from Redis
    if refresh_token:
        try:
            payload = utils.verify_refresh_token(refresh_token)
            if payload and payload.get("email"):
                utils.delete_refresh_token(payload["email"])
        except Exception as e:
            print(f"Error deleting refresh token: {e}")
    
    # Clear the refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}



# 1. Forgot password - generate JWT token and store in Redis
@app.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing forgot password for email: {request.email}")

        # Check if user exists
        user = db.query(UserTable).filter(UserTable.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Email not registered")

        # Generate JWT token
        jwt_token = utils.create_reset_token(request.email)
        logger.info(f"Generated JWT token for user: {user.full_name}")

        # Store JWT token in Redis with expiry (900 seconds = 15 minutes)
        try:
            redis_key = f"reset_token:{jwt_token}"
            # redis_client.setex(redis_key, 900, request.email)           
            logger.info(f"JWT token stored in Redis successfully")
        except Exception as redis_error:
            logger.error(f"Redis error: {str(redis_error)}")
            raise HTTPException(status_code=500, detail="Failed to store reset token")

        # Create reset link with JWT token
        reset_link = f"{frontend_url}/reset-password-form?token={jwt_token}"

        # Prepare email message with HTML
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Password Reset Request</h2>
                    
                    <p>Hello <strong>{user.full_name}</strong>,</p>
                    
                    <p>You have requested to reset your password. Please click the button below to reset your password:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background-color: #2563eb; 
                                  color: white; 
                                  padding: 12px 30px; 
                                  text-decoration: none; 
                                  border-radius: 5px; 
                                  display: inline-block;
                                  font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #2563eb;">
                        <a href="{reset_link}" style="color: #2563eb;">{reset_link}</a>
                    </p>
                    
                    <p style="color: #ef4444; font-weight: bold;">⏰ This link will expire in 15 minutes for security reasons.</p>
                    
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    
                    <p style="color: #6b7280; font-size: 14px;">
                        Best regards,<br>
                        <strong>Concientech IT Solutions</strong><br>
                        Haridwar 249404
                    </p>
                </div>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[request.email],
            body=html_body,
            subtype=MessageType.html
        )

        # Send email
        try:
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info("Password reset email sent successfully")
        except Exception as email_error:
            logger.error(f"Email sending error: {str(email_error)}")
            # Clean up the token from Redis if email fails
            # redis_client.delete(f"reset_token:{jwt_token}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(email_error)}")
        return {
                    "message": "Password reset link sent to your email.", 
                    "token_type": "JWT", 
                    "token" : jwt_token
                }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in forgot_password: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")


# NEW: Reset password route using JWT token
@app.post("/reset-password")
async def reset_password_confirm(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Reset password using JWT reset token and new password
    """
    try:
        logger.info(f"Processing password reset confirm for token: {request.token[:10]}...")

        # Verify the reset token
        try:
            payload = utils.verify_reset_token(request.token)  # Assuming this method exists in token_utils
            email = payload.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Invalid reset token")
        except Exception as token_error:
            logger.error(f"Token verification failed: {str(token_error)}")
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        # Check if user exists
        user = db.query(UserTable).filter(UserTable.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Hash the new password
        hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password in database
        user.password = hashed_password.decode('utf-8')
        db.commit()
        db.refresh(user)

        # Clean up the reset token from Redis
        try:
            redis_key = f"reset_token:{request.token}"
            # redis_client.delete(redis_key)  # Redis cleanup
            logger.info("Reset token cleaned up from Redis")
        except Exception as redis_error:
            logger.error(f"Redis cleanup error (non-critical): {str(redis_error)}")

        logger.info(f"Password reset successful for user: {user.email}")
        
        return {
            "message": "Password reset successfully",
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in reset_password_confirm: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error occurred")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


Base.metadata.create_all(bind=engine)