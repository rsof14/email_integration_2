import math
from fastapi.websockets import WebSocket, WebSocketState
from sqlalchemy.orm import Session
from ..api.models.messages import Page
from ..db.queries.emails import get_last_message, get_user_emails_page, get_all_emails, write_message
from .email_observers import DatabaseEmailObserver, WebsocketEmailObserver
from .email_fetcher import EmailFetcher
from .email_collection import EmailCollection


async def check_password(email: str, password: str):
    try:
        async with EmailFetcher(email=email, password=password):
            return True
    except Exception as e:
        # TODO: log e
        return False


async def check_mailbox(email: str, password: str, db: Session, ws_connection: WebSocket):
    try:
        last_message = get_last_message(db, email)
        since_date = last_message.date if last_message else None
        async with EmailFetcher(email=email, password=password, since_date=since_date) as fetcher:
            email_collection = EmailCollection(fetcher=fetcher)
            db_observer = DatabaseEmailObserver(db)
            ws_observer = WebsocketEmailObserver(ws_connection)
            email_collection.subscribe(db_observer)
            email_collection.subscribe(ws_observer)
            await email_collection.list_emails()
    except Exception as e:
        if ws_connection.application_state == WebSocketState.CONNECTED and ws_connection.client_state == WebSocketState.CONNECTED:
            await ws_connection.send_text(f'Ошибка при получении писем: {str(e)}')
            # log(e)
        else:
            # log(e)
            pass
        # 1. Если ошибка произошла НЕ с вебсокетом и вебсокет жив, то отправить ошибку в вебсокет
        # 2. Если ошибка произошла с вебсокет соединением, залогировать ошибку


def get_user_emails(email: str, page: Page, db):
    emails = get_user_emails_page(db=db, email=email, page_from=page.page_from, page_size=page.page_size)
    return emails


def get_pages_num(email: str, page: Page, db):
    emails_count = get_all_emails(db=db, email=email)
    return math.ceil(emails_count / page.page_size)
