from http import HTTPStatus
from fastapi import APIRouter, Depends, Request
from jose import JWTError
from services.passwords import decode_jwt, IncorrectAccessToken
from sqlalchemy.orm import Session
from db.pg_db import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from typing import Annotated


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def get_emails(request: Request, token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    try:
        payload = decode_jwt(token)
    except Exception:
        return templates.TemplateResponse(
            request=request, name="login.html"
        )

    return templates.TemplateResponse(
                request=request, name="main.html", context={"email": payload.get("email")}
            )