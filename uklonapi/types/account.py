from pydantic import BaseModel


class Auth(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    client_id: str
    expires_in: int
    expires: str
    issued: str
