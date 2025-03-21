from datetime import datetime
from aioimaplib import aioimaplib
from ..utils.email_utils import get_imap_server, parse_message


class EmailFetcher:
    email: str
    password: str
    since_date: datetime | None
    server: str | None
    client: aioimaplib.IMAP4_SSL | None

    def __init__(self, email: str, password: str, since_date: datetime|None = None):
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
        await self.client.logout()

    async def __aiter__(self):
        self.messages = []
        status, data = await self.client.select('INBOX')
        if self.since_date:
            since_date_imap = self.since_date.strftime('%d-%b-%Y')
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