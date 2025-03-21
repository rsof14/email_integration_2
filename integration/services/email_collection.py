from .email_observers import EmailObserver
from .email_fetcher import EmailFetcher


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