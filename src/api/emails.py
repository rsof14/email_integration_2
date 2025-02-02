from http import HTTPStatus
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from .models.login import LoginRequest, Token
from services.passwords import decode_jwt, IncorrectAccessToken
from sqlalchemy.orm import Session
from db.pg_db import get_db
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/')
async def get_emails(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_jwt(token)
    return {"email": payload.get("email")}