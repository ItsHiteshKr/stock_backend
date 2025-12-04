from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os
import secrets
from datetime import datetime
import logging

from db.database import get_db
import model.user_model as usermodels
from router.user_router import router as user_router
from admin.user_routes import router as admin_user_router


# Set up logging
logging.basicConfig(level=logging.INFO)
from starlette.middleware.sessions import SessionMiddleware
# Define the FastAPI app
admin_panel = FastAPI(title="Concientech Admin")

# Include routers
admin_panel.include_router(user_router, prefix="/api/user")
admin_panel.include_router(admin_user_router, prefix="/user")

# Add session middleware
admin_panel.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("ADMIN_SECRET_KEY", "supersecret"),
    max_age=3600  # 1 hour session expiry
)

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Secure admin credentials (in a real app, store these securely)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Import admin auth utilities
from .auth_utils import admin_required, get_current_admin

# Mount static files
admin_panel.mount("/static", StaticFiles(directory="static"), name="static")

# Login route - GET (show login form)
@admin_panel.get("/login", response_class=HTMLResponse)
async def admin_login_form(request: Request, admin_username: Optional[str] = Depends(get_current_admin)):
    # If already logged in, redirect to dashboard
    if admin_username:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": None})

# Login route - POST (process login form)
@admin_panel.post("/login", response_class=HTMLResponse)
async def admin_login_submit(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...)
):
    # Validate credentials
    is_username_correct = secrets.compare_digest(username, ADMIN_USERNAME)
    is_password_correct = secrets.compare_digest(password, ADMIN_PASSWORD)
    
    if not (is_username_correct and is_password_correct):
        return templates.TemplateResponse(
            "admin/login.html", 
            {"request": request, "error": "Invalid credentials"}
        )
    
    # Set session
    request.session["admin_username"] = username
    request.session["login_time"] = datetime.now().isoformat()
    
    # Redirect to dashboard
    return RedirectResponse(url="/admin/dashboard", status_code=302)

# Logout route
@admin_panel.get("/logout")
async def admin_logout(request: Request):
    # Clear specific session data
    request.session.pop("admin_username", None)
    request.session.pop("login_time", None)

    # Create response with redirect
    response = RedirectResponse(url="/admin/login", status_code=303)

    # Clear session cookie
    response.delete_cookie("session", path="/")

    # Clear session cookie by setting it to expire immediately
    response.delete_cookie("session")

    return response

# Root route
@admin_panel.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    # Check if user is authenticated
    admin_username = request.session.get("admin_username")
    if admin_username:
        # If authenticated, go to dashboard
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    else:
        
        return RedirectResponse(url="/admin/login", status_code=302)

# Dashboard route - Shows dashboard.html with stats and user list
@admin_panel.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    admin_username: str = Depends(admin_required), 
    db: Session = Depends(get_db)
):
    try:
        # Get user statistics and all users for the table
        user_count = db.query(usermodels.UserTable).count()
        users = db.query(usermodels.UserTable).order_by(usermodels.UserTable.id).all()

        logging.info(f"Dashboard: Found {user_count} total users")
        
        # Return dashboard.html with all necessary data
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "admin_name": admin_username,
                "user_count": user_count,
                "users": users,  # For the users table
                "error": None
            }
        )
    except Exception as e:
        logging.error(f"Dashboard Error: {str(e)}")
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "admin_name": admin_username,
                "user_count": 0,
                "users": [],
                "error": str(e)
            }
        )

# Users list route
@admin_panel.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    admin_username: str = Depends(admin_required),
    db: Session = Depends(get_db)
):
    try:
        users = db.query(usermodels.UserTable).all()
        logging.info(f"Found {len(users)} users")
        
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "admin_name": admin_username,
                "users": users,
                "error": None
            }
        )
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "admin_name": admin_username,
                "users": [],
                "error": str(e)
            }
        )
