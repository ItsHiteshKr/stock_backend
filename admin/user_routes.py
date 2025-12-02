from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt
import logging

from db.database import get_db
import model.user_model as usermodels
from .auth_utils import admin_required


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/user_details", response_class=HTMLResponse)
async def list_users(
    request: Request,
    admin_username: str = Depends(admin_required),
    db: Session = Depends(get_db)
):
    try:
        # Get page from query parameters, default to 1
        page = int(request.query_params.get("page", 1))
        items_per_page = 10  # Number of users per page

        # Get total count and paginated users with proper ordering
        user_query = db.query(usermodels.UserTable).order_by(usermodels.UserTable.id)
        total_users = user_query.count()
        users = user_query.offset((page - 1) * items_per_page).limit(items_per_page).all()
        total_pages = (total_users + items_per_page - 1) // items_per_page

        logging.info(f"Users page: Found {total_users} users, showing page {page} of {total_pages}")
        
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "admin_name": admin_username,
                "users": users,
                "page": page,
                "total_pages": total_pages,
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
                "page": 1,
                "total_pages": 1,
                "error": str(e)
            }
        )

@router.get("/new", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    admin_username: str = Depends(admin_required),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "admin/user/create_user_form.html",
        {
            "request": request,
            "admin_name": admin_username,
            "error": None
        }
    )

@router.post("/new", response_class=HTMLResponse)
async def create_user(
    request: Request,
    admin_username: str = Depends(admin_required),
    db: Session = Depends(get_db)
):
    try:
        form = await request.form()
        full_name = form.get("full_name")
        email = form.get("email")
        password = form.get("password")
        
        # Validate required fields
        if not all([full_name, email, password]):
            return templates.TemplateResponse(
                "admin/user/create_user_form.html",
                {
                    "request": request,
                    "admin_name": admin_username,
                    "roles": ["user", "admin"],
                    "error": "All fields are required"
                }
            )

        # Check if user already exists
        existing_user = db.query(usermodels.UserTable).filter(
            (usermodels.UserTable.full_name == full_name) | (usermodels.UserTable.email == email)
        ).first()

        if existing_user:
            return templates.TemplateResponse(
                "admin/user/create_user_form.html",
                {
                    "request": request,
                    "admin_name": admin_username,
                    "roles": ["user", "admin"],
                    "error": "User with this username or email already exists"
                }
            )

        # Create new user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = usermodels.User(
            full_name=full_name,
            email=email,
            password=hashed_password.decode('utf-8')
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return RedirectResponse(url="/admin/user/users", status_code=303)

    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")

@router.get("/view/{user_id}", response_class=HTMLResponse)
async def view_user(
    request: Request,
    user_id: int,
    admin_username: str = Depends(admin_required),
    db: Session = Depends(get_db)
):
    try:
        # Get user and their details
        user = db.query(usermodels.UserTable).filter(usermodels.UserTable.id == user_id).first()
        if not user:
            logging.error(f"User not found: {user_id}")
            return RedirectResponse(url="/admin/user/user_details", status_code=303)
            
        logging.info(f"Viewing user details for user ID: {user_id}")
        return templates.TemplateResponse(
            "admin/user/user_detail.html",
            {
                "request": request,
                "admin_name": admin_username,
                "user": user,
            }
        )
    except Exception as e:
        logging.error(f"Error viewing user: {str(e)}")
        return RedirectResponse(url="/admin/user/user_details", status_code=303)

