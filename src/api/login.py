from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Form
from .models.login import LoginRequest
from services.login_service import login_user, UserIncorrectLoginData
from sqlalchemy.orm import Session
from db.pg_db import get_db
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starsessions import load_session


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/')
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post('/')
async def login(request: Request, data: Annotated[LoginRequest, Form()], db: Annotated[Session, Depends(get_db)]):
    try:
        await load_session(request)
        user_data = await login_user(data, db)
        request.session['email'] = user_data['email']
        request.session['password'] = user_data['password']
    except UserIncorrectLoginData as err:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": err})

    return RedirectResponse("/email", status_code=303)