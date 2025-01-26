from http import HTTPStatus
from fastapi import APIRouter, Depends
from .models.login import LoginRequest

router = APIRouter()

@router.post('/')
async def login(data: LoginRequest):
    pass