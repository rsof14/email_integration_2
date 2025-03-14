import base64
import json
from datetime import datetime, timedelta
from imapclient import IMAPClient
from imapclient.exceptions import LoginError, IMAPClientError
from aioimaplib import aioimaplib
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz
from email import message_from_bytes
from db.queries.emails import write_messages, get_last_message, get_user_emails_page, get_all_emails
from core.config import app_config
from src.api.models.messages import Page
import math
from fastapi.websockets import WebSocket
from sqlalchemy.orm import sessionmaker
from utils.email_utils import get_imap_server, decode_mime_words, parse_message


class EmailFetcher:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def __setattr__(self, key, value):
        if key == 'email':
            self.server = get_imap_server(self.email)

    async def __aenter__(self):
        self.client = aioimaplib.IMAP4_SSL(host=self.server)
        await self.client.login(self.email, self.password)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
        await self.client.logout()

    async def __aiter__(self):
        self.messages = []
        last_message = get_last_message(db, self.email)
        since_date = last_message.date if last_message else None
        status, data = await self.client.select('INBOX')
        if since_date:
            since_date_imap = datetime.strptime(since_date, "%Y-%m-%dT%H:%M:%S").strftime('%d-%b-%Y')
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
        else:
            raise StopIteration('All messages have been fetched')



def check_password(email: str, password: str):
    try:
        server = get_imap_server(email)
        client = IMAPClient(server).login(username=email, password=password)
    except (LoginError, GettingIMAPServerError):
        return False

    return True



async def check_mailbox(email: str, password: str, db: sessionmaker, ws_connection: WebSocket):
    messages_list = []
    server = get_imap_server(email)
    imap_client = aioimaplib.IMAP4_SSL(host=server)
    try:
        await imap_client.wait_hello_from_server()
        await imap_client.login(email, password)
    except IMAPClientError:
        await ws_connection.send_text('An error occurred while connecting to the mails server.')

    last_message = get_last_message(db, email)
    since_date = last_message.date if last_message else None
    status, data = await imap_client.select('INBOX')
    if status != "OK":
        await ws_connection.send_text('Failed to receive emails.')
        return
    if since_date:
        since_date_imap = datetime.strptime(since_date, "%Y-%m-%dT%H:%M:%S").strftime('%d-%b-%Y')
        criteria = f'(SINCE {since_date_imap})'
    else:
        criteria = 'ALL'
    status, messages = await imap_client.search(criteria)
    if status != "OK" or not messages[0]:
        return
    emails_ids = messages[0].decode().split()
    for email_id in emails_ids:
        status, msg_data = await imap_client.fetch(email_id, 'RFC822')
        if status != "OK":
            continue

        msg = message_from_bytes(msg_data[1])
        email_date = datetime(*parsedate_tz(msg["Date"])[:6])
        if since_date and email_date <= datetime.strptime(since_date, "%Y-%m-%dT%H:%M:%S"):
            continue
        msg_from = msg["Return-path"]
        header_row = decode_header(msg["Subject"])[0][0] if msg["Subject"] else ''
        try:
            header = header_row.decode()
        except AttributeError:
            header = header_row
        message_text = ''
        for part in msg.walk():
            if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                message_text = base64.b64decode(part.get_payload()).decode()
        messages_list.append({'date': email_date, 'from_email': msg_from, 'topic': header, 'message_text': message_text})
        if len(messages_list) >= app_config.MESSAGES_BATCH_SIZE:
            write_messages(db, email, messages_list)
            emails = get_user_emails_page(db=db, email=email, page_from=1, page_size=app_config.DEFAULT_PAGE_SIZE)
            json_data = json.dumps(list(map(lambda message: message.to_dict(), emails)))
            await ws_connection.send_text(json_data)
            messages_list = []
    write_messages(db, email, messages_list)
    emails = get_user_emails_page(db=db, email=email, page_from=1, page_size=app_config.DEFAULT_PAGE_SIZE)
    json_data = json.dumps(list(map(lambda message: message.to_dict(), emails)))
    await ws_connection.send_text(json_data)

    await imap_client.logout()


def get_user_emails(email: str, page: Page, db):
    emails = get_user_emails_page(db=db, email=email, page_from=page.page_from, page_size=page.page_size)
    return emails


def get_pages_num(email: str, page: Page, db):
    emails = get_all_emails(db=db, email=email)
    return math.ceil(len(emails) / page.page_size)