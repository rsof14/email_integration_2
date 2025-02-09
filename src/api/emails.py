from fastapi import APIRouter, Depends, Request, Cookie
from services.login_service import get_user_data_from_session
from sqlalchemy.orm import Session
from db.pg_db import get_db
from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi.responses import RedirectResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def get_emails(request: Request, db: Annotated[Session, Depends(get_db)], session_id: str = Cookie(None)):
    user_data = await get_user_data_from_session(session_id)
    if not user_data:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
                request=request, name="main.html", context={"email": user_data['email']}
            )