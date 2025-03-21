from typing import Annotated
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .models.login import LoginRequest
from ..db.pg_db import get_db
from ..services.login_service import login_user, UserIncorrectLoginData
from ..templates import templates


router = APIRouter()


@router.get('/')
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post('/')
async def login(request: Request, data: Annotated[LoginRequest, Form()], db: Annotated[Session, Depends(get_db)]):
    try:
        user_data = await login_user(data, db)
        request.session['email'] = user_data['email']
        request.session['password'] = user_data['password']
    except UserIncorrectLoginData as err:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": err})

    return RedirectResponse("/email", status_code=303)
