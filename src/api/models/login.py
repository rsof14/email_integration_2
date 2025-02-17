from core.base_model import OrjsonBaseModel


class LoginRequest(OrjsonBaseModel):
    email: str
    password: str


class Token(OrjsonBaseModel):
    access_token: str
    token_type: str
