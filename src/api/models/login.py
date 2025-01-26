from uuid import UUID
from typing import Union

from core.base_model import OrjsonBaseModel


class LoginRequest(OrjsonBaseModel):
    email: str
    password: str