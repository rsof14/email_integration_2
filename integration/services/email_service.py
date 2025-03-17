import json
import math
from fastapi.websockets import WebSocket
from sqlalchemy.orm import sessionmaker, Session
from ..api.models.messages import Page
from ..core.config import app_config
from ..db.queries.emails import get_last_message, get_user_emails_page, get_all_emails, write_message
from email_observers import EmailObserver
from email_fetcher import EmailFetcher
from email_collection import EmailCollection


async def check_password(email: str, password: str):
    try:
        async with EmailFetcher(email=email, password=password):
            return True
    except Exception as e:
        # TODO: log e
        return False


async def send_message_to_ws(email: str, message_data: dict, ws_connection: WebSocket, db: sessionmaker):
    write_message(db, email, message_data)
    emails = get_user_emails_page(db=db, email=email, page_from=1, page_size=app_config.DEFAULT_PAGE_SIZE)
    json_data = json.dumps(list(map(lambda message: message.to_dict(), emails)))
    await ws_connection.send_text(json_data)


async def check_mailbox(email: str, password: str, db: Session, ws_connection: WebSocket):
    try:
        last_message = get_last_message(db, email)
        since_date = last_message.date if last_message else None
        async with EmailFetcher(email=email, password=password, since_date=since_date) as fetcher:
            observer = EmailObserver(update=send_message_to_ws, ws_connection = ws_connection)
            email_collection = EmailCollection(fetcher=fetcher)
            email_collection.subscribe(observer)
            await email_collection.list_emails()
    except:
        # 1. Если ошибка произошла НЕ с вебсокетом и вебсокет жив, то отправить ошибку в вебсокет
        # 2. Если ошибка произошла с вебсокет соединением, залогировать ошибку
        pass  # TODO: обработать исключительную ситуацию


def get_user_emails(email: str, page: Page, db):
    emails = get_user_emails_page(db=db, email=email, page_from=page.page_from, page_size=page.page_size)
    return emails


def get_pages_num(email: str, page: Page, db):
    emails_count = get_all_emails(db=db, email=email)
    return math.ceil(emails_count / page.page_size)
