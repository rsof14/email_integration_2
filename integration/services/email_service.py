import json
import math
from datetime import datetime

from fastapi.websockets import WebSocket
from sqlalchemy.orm import sessionmaker, Session
from aioimaplib import aioimaplib
from ..api.models.messages import Page
from ..core.config import app_config
from ..db.queries.emails import get_last_message, get_user_emails_page, get_all_emails, write_message
from ..utils.email_utils import get_imap_server, parse_message


class EmailFetcher:
    email: str
    password: str
    since_date: str | None
    server: str | None
    client: aioimaplib.IMAP4_SSL | None

    def __init__(self, email: str, password: str, since_date: str|None = None):
        self.email = email
        self.password = password
        self.since_date = since_date
        self.server = None
        self.client = None

    async def __aenter__(self):
        self.server = get_imap_server(self.email)
        self.client = aioimaplib.IMAP4_SSL(host=self.server)
        await self.client.wait_hello_from_server()
        await self.client.login(self.email, self.password)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # await self.client.close()
        await self.client.logout()

    async def __aiter__(self):
        self.messages = []
        status, data = await self.client.select('INBOX')
        if self.since_date:
            since_date_imap = datetime.strptime(self.since_date, "%Y-%m-%dT%H:%M:%S").strftime('%d-%b-%Y')
            criteria = f'(SINCE {since_date_imap})'
        else:
            criteria = 'ALL'
        status, messages = await self.client.search(criteria)
        emails_ids = messages[0].decode().split() if messages[0] else []
        for email_id in emails_ids:
            status, msg_data = await self.client.fetch(email_id, 'RFC822')
            if status != "OK":
                continue
            message = parse_message(msg_data)
            self.messages.append(message)

        return self

    async def __anext__(self):
        if self.messages:
            return self.messages.pop()
        raise StopIteration('All messages have been fetched')


class EmailObserver:
    def __init__(self, update: callable, **kwargs):
        self.update = update
        self.kwargs = kwargs

    def notify(self, email: str, message: dict):
        self.update(email, message, **self.kwargs)

# class EmailObserver(Protocol):
#     @abstractmethod
#     def notify(self, email: str, message: dict):
#         pass
#
#
# class DatabaseEmailObserver(EmailObserver):
#     def __init__(self):
#         pass
#
#     @override
#     def notify(self, email: str, message: dict):
#         pass # обрабатываем письмо, сохраняя в БД
#
#
# class WebsocketEmailObserver(EmailObserver):
#     def __init__(self):
#         pass
#
#     @override
#     def notify(self, email: str, message: dict):
#         pass # обрабатываем письмо, отправляя уведомление в вебсокет


class EmailCollection:
    __observers: list[EmailObserver]
    __fetcher: EmailFetcher

    def __init__(self, fetcher: EmailFetcher):
        self.__observers = []
        self.__fetcher = fetcher

    def subscribe(self, observer: EmailObserver):
        self.__observers.append(observer)

    async def list_emails(self):
        async for message in self.__fetcher:
            for observer in self.__observers:
                observer.notify(self.__fetcher.email, message)


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
    emails = get_all_emails(db=db, email=email)
    return math.ceil(len(emails) / page.page_size)

#
#
# def check_password(email: str, password: str):
#     try:
#         server = get_imap_server(email)
#         client = IMAPClient(server).login(username=email, password=password)
#     except (LoginError, GettingIMAPServerError):
#         return False
#
#     return True
#
#
#
# async def check_mailbox(email: str, password: str, db: sessionmaker, ws_connection: WebSocket):
#     messages_list = []
#     server = get_imap_server(email)
#     imap_client = aioimaplib.IMAP4_SSL(host=server)
#     try:
#         await imap_client.wait_hello_from_server()
#         await imap_client.login(email, password)
#     except IMAPClientError:
#         await ws_connection.send_text('An error occurred while connecting to the mails server.')
#
#     last_message = get_last_message(db, email)
#     since_date = last_message.date if last_message else None
#     status, data = await imap_client.select('INBOX')
#     if status != "OK":
#         await ws_connection.send_text('Failed to receive emails.')
#         return
#     if since_date:
#         since_date_imap = datetime.strptime(since_date, "%Y-%m-%dT%H:%M:%S").strftime('%d-%b-%Y')
#         criteria = f'(SINCE {since_date_imap})'
#     else:
#         criteria = 'ALL'
#     status, messages = await imap_client.search(criteria)
#     if status != "OK" or not messages[0]:
#         return
#     emails_ids = messages[0].decode().split()
#     for email_id in emails_ids:
#         status, msg_data = await imap_client.fetch(email_id, 'RFC822')
#         if status != "OK":
#             continue
#
#         msg = message_from_bytes(msg_data[1])
#         email_date = datetime(*parsedate_tz(msg["Date"])[:6])
#         if since_date and email_date <= datetime.strptime(since_date, "%Y-%m-%dT%H:%M:%S"):
#             continue
#         msg_from = msg["Return-path"]
#         header_row = decode_header(msg["Subject"])[0][0] if msg["Subject"] else ''
#         try:
#             header = header_row.decode()
#         except AttributeError:
#             header = header_row
#         message_text = ''
#         for part in msg.walk():
#             if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
#                 message_text = base64.b64decode(part.get_payload()).decode()
#         messages_list.append({'date': email_date, 'from_email': msg_from, 'topic': header, 'message_text': message_text})
#         if len(messages_list) >= app_config.MESSAGES_BATCH_SIZE:
#             write_messages(db, email, messages_list)
#             emails = get_user_emails_page(db=db, email=email, page_from=1, page_size=app_config.DEFAULT_PAGE_SIZE)
#             json_data = json.dumps(list(map(lambda message: message.to_dict(), emails)))
#             await ws_connection.send_text(json_data)
#             messages_list = []
#     write_messages(db, email, messages_list)
#     emails = get_user_emails_page(db=db, email=email, page_from=1, page_size=app_config.DEFAULT_PAGE_SIZE)
#     json_data = json.dumps(list(map(lambda message: message.to_dict(), emails)))
#     await ws_connection.send_text(json_data)
#
#     await imap_client.logout()


