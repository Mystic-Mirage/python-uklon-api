from functools import cached_property

import jwt
from pydantic import BaseModel


class Auth(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    client_id: str
    expires_in: int
    expires: str
    issued: str

    @cached_property
    def access_token_exp(self):
        return jwt.decode(self.access_token, options={"verify_signature": False})["exp"]
