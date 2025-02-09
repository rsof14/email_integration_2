from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from .models.login import LoginRequest, Token
from services.login_service import login_user, UserIncorrectLoginData
from sqlalchemy.orm import Session
from db.pg_db import get_db
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/')
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post('/')
async def login(request: Request, response: Response, db: Annotated[Session, Depends(get_db)]):
    try:
        form_data = await request.form()
        data = LoginRequest(**dict(form_data))
        session_id = await login_user(data, db)
        response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")
    except UserIncorrectLoginData as err:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return RedirectResponse("/email", status_code=302)
    # return templates.TemplateResponse(request=request, name="main.html")