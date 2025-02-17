from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starsessions import load_session


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def get_emails(request: Request):
    user_email = request.session.get('email', None)
    if not user_email:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
                request=request, name="main.html", context={"email": user_email}
            )