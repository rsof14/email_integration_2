from datetime import datetime, timedelta
import orjson
from imapclient import IMAPClient
from urllib.request import urlopen
from imapclient.exceptions import LoginError
from aioimaplib import aioimaplib
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz
from email import message_from_bytes


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


async def check_mailbox(email: str, password: str, since_date: str = None):
    print('started checking mailbox')
    server = get_imap_server(email)
    imap_client = aioimaplib.IMAP4_SSL(host=server)
    await imap_client.wait_hello_from_server()
    await imap_client.login(email, password)

    status, data = await imap_client.select('INBOX')
    if status != "OK":
        return None
    if since_date:
        since_date_imap = datetime.strptime(since_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        criteria = f'(SINCE {since_date_imap})'
    else:
        # criteria = 'ALL'
        since_date_imap = (datetime.now() - timedelta(days=2)).strftime('%d-%b-%Y')
        criteria = f'(SINCE {since_date_imap})'
        print(criteria)
    status, messages = await imap_client.search(criteria)
    print(f'status {status} messages {messages}')
    if status != "OK" or not messages[0]:
        print('no messages')
        return None
    emails_ids = messages[0].decode().split()
    for email_id in emails_ids:
        status, msg_data = await imap_client.fetch(email_id, 'RFC822')
        if status != "OK":
            print(f'не удалось получить письмо с id {email_id}')
            continue

        msg = message_from_bytes(msg_data[1])
        email_date = datetime(*parsedate_tz(msg["Date"])[:6])
        print(f'email date {email_date} with type {type(email_date)}')
        since_date = '2025-02-22 17:00:00'
        if since_date and email_date <= datetime.strptime(since_date, '%Y-%m-%d %H:%M:%S'):
            print('!!!')
            continue
        msg_from = msg["Return-path"]
        header = decode_header(msg["Subject"])[0][0].decode() if msg["Subject"] else ''

        print(f'header {header} date {email_date} from {msg_from}')


    await imap_client.logout()
