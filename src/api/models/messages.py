from core.config import app_config
from fastapi import Query
from core.base_model import OrjsonBaseModel


class Page:
    def __init__(
            self,
            page_size: int = Query(app_config.DEFAULT_PAGE_SIZE, ge=1),
            page_number: int = Query(1, ge=1)
    ) -> None:
        self.page_size = page_size
        self.page_number = page_number

    @property
    def page_from(self):
        return self.page_size * (self.page_number - 1)


class Message(OrjsonBaseModel):
    date: str
    from_email: str
    topic: str
    message_text: str
    attachments: str|None