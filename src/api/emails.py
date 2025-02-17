import asyncio
from typing import Dict
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect


router = APIRouter()
templates = Jinja2Templates(directory="templates")
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f'ws {websocket.session}')
    active_connections[websocket.session['email']] = websocket
    try:
        while True:
            await websocket.send_json({'msg': 'test connection'})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        active_connections.pop(websocket.session['email'], None)


@router.get('/')
async def get_emails(request: Request):
    user_email = request.session.get('email', None)
    if not user_email:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
                request=request, name="main.html", context={"email": user_email}
            )