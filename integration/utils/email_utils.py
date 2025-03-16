import base64
import ssl
from datetime import datetime

import orjson
from urllib.request import urlopen
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz
from email import message_from_bytes


ssl._create_default_https_context = ssl._create_stdlib_context


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


def decode_mime_words(s):
    decoded_fragments = decode_header(s)
    return ''.join(
        fragment.decode(encoding or 'utf-8') if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    )


def parse_message(msg_data: tuple[str]):
    msg = message_from_bytes(msg_data[1])
    email_date = datetime(*parsedate_tz(msg["Date"])[:6])
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
    return {'date': email_date, 'from_email': msg_from, 'topic': header, 'message_text': message_text}
