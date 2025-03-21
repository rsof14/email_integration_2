import asyncio
from typing import Dict, Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi import BackgroundTasks
from http import HTTPStatus
from sqlalchemy.orm import Session
from .models.messages import Page
from ..db.pg_db import get_db
from ..services.email_service import check_mailbox, get_user_emails, get_pages_num


router = APIRouter()
templates = Jinja2Templates(directory="templates")
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_email = websocket.session['email']
    active_connections[user_email] = websocket
    try:
        while True:
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        active_connections.pop(user_email, None)


@router.post('/update')
def update_emails(request: Request, db: Annotated[Session, Depends(get_db)], background_tasks: BackgroundTasks):
    user_email = request.session.get('email', None)
    user_password = request.session.get('password', None)
    if user_email and user_password:
        background_tasks.add_task(check_mailbox, user_email, user_password, db, active_connections.get(user_email))
        return {"message": "Updating emails"}, HTTPStatus.ACCEPTED
    else:
        return {"message": "Auth required"}, HTTPStatus.UNAUTHORIZED


@router.get('/')
async def get_emails(request: Request, db: Annotated[Session, Depends(get_db)], page: Page = Depends()):
    user_email = request.session.get('email', None)
    if not user_email:
        return RedirectResponse("/login", status_code=302)
    emails = get_user_emails(email=user_email, page=page, db=db)
    pages_num = get_pages_num(email=user_email, page=page, db=db)
    return templates.TemplateResponse(
                request=request, name="main.html", context={"emails": emails, "current_page": page.page_number,
                                                            "pages_num": pages_num}
            )
