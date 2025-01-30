from http import HTTPStatus
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from .models.login import LoginRequest
from services.login_service import login_user, UserIncorrectLoginData
from sqlalchemy.orm import Session
from db.pg_db import get_db


router = APIRouter()


@router.post('/')
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return await login_user(data, db)
    except UserIncorrectLoginData as err:
        return JSONResponse(content={"message": str(err)}, status_code=HTTPStatus.UNAUTHORIZED)