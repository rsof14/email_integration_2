import base64
from datetime import datetime, timedelta
import orjson
from imapclient import IMAPClient
from urllib.request import urlopen
from imapclient.exceptions import LoginError
from aioimaplib import aioimaplib
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz
from email import message_from_bytes
from db.queries.emails import write_messages, get_last_message, get_user_emails_page
from core.config import app_config
from src.api.models.messages import Page


class GettingIMAPServerError(Exception):
    ...


def get_imap_server(email: str):
    with urlopen('https://emailsettings.firetrust.com/settings?q=' + email) as response:
        if response.getcode() == 200:
            source = response.read()
            data = orjson.loads(source)
            for i in range(0, len(data["settings"]) + 1):
                if data["settings"][i]["protocol"] == "IMAP":
                    imap_server = data["settings"][i]["address"]
                    return imap_server

    raise GettingIMAPServerError()


def check_password(email: str, password: str):
    try:
        server = get_imap_server(email)
        client = IMAPClient(server).login(username=email, password=password)
    except (LoginError, GettingIMAPServerError):
        return False

    return True


def decode_mime_words(s):
    decoded_fragments = decode_header(s)
    return ''.join(
        fragment.decode(encoding or 'utf-8') if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    )


async def check_mailbox(email: str, password: str, db):
    messages_list = []
    server = get_imap_server(email)
    imap_client = aioimaplib.IMAP4_SSL(host=server)
    await imap_client.wait_hello_from_server()
    await imap_client.login(email, password)

    last_message = get_last_message(db, email)
    since_date = last_message.date if last_message else None
    status, data = await imap_client.select('INBOX')
    if status != "OK":
        return None
    if since_date:
        since_date_imap = since_date.strftime('%d-%b-%Y')
        criteria = f'(SINCE {since_date_imap})'
    else:
        criteria = 'ALL'
    status, messages = await imap_client.search(criteria)
    if status != "OK" or not messages[0]:
        return None
    emails_ids = messages[0].decode().split()
    for email_id in emails_ids:
        status, msg_data = await imap_client.fetch(email_id, 'RFC822')
        if status != "OK":
            print(f'не удалось получить письмо с id {email_id}')
            continue

        msg = message_from_bytes(msg_data[1])
        email_date = datetime(*parsedate_tz(msg["Date"])[:6])
        if since_date and email_date <= since_date:
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
            messages_list = []
    write_messages(db, email, messages_list)

    await imap_client.logout()


def get_user_emails(email: str, page: Page, db):
    emails = get_user_emails_page(db, email, page.page_from, page.page_size)
    return emails