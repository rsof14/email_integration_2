from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from .models.login import LoginRequest, Token
from services.login_service import login_user, UserIncorrectLoginData
from sqlalchemy.orm import Session
from db.pg_db import get_db


router = APIRouter()


@router.post('/', response_model=Token)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        tokens = await login_user(data, db)
    except UserIncorrectLoginData as err:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens