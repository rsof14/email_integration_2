from abc import abstractmethod
from typing import Protocol, override


class EmailObserver(Protocol):
    @abstractmethod
    def notify(self, email: str, message: dict):
        pass


class DatabaseEmailObserver(EmailObserver):
    def __init__(self):
        pass

    @override
    def notify(self, email: str, message: dict):
        pass # обрабатываем письмо, сохраняя в БД


class WebsocketEmailObserver(EmailObserver):
    def __init__(self):
        pass

    @override
    def notify(self, email: str, message: dict):
        pass # обрабатываем письмо, отправляя уведомление в вебсокет