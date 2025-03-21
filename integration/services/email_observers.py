from abc import abstractmethod
from typing import Protocol, override
import json
from ..db.queries.emails import write_message


class EmailObserver(Protocol):
    @abstractmethod
    def notify(self, email: str, message: dict):
        pass


class DatabaseEmailObserver(EmailObserver):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    @override
    def notify(self, email: str, message: dict):
        write_message(self.db_connection, email, message) # обрабатываем письмо, сохраняя в БД


class WebsocketEmailObserver(EmailObserver):
    def __init__(self, ws_connection):
        self.ws_connection = ws_connection

    @override
    async def notify(self, email: str, message: dict):
        json_data = json.dumps(message)
        await self.ws_connection.send_text(json_data) # обрабатываем письмо, отправляя уведомление в вебсокет