from datetime import datetime

import orjson
from imapclient import IMAPClient
from urllib.request import urlopen
from imapclient.exceptions import LoginError
from aioimaplib import aioimaplib


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
        since_date_obj = datetime.strptime(since_date, '%Y-%m-%d')
        since_date_imap = since_date_obj.strftime('%d-%b-%Y')
        criteria = f'(SINCE {since_date_imap})'
    else:
        # criteria = 'ALL'
        criteria = "('SINCE' 20-02-2025)"
    status, messages = await imap_client.search('SINCE 20-Feb-2025')
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

        print(msg_data)

    await imap_client.logout()
