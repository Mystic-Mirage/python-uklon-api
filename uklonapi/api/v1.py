from .base import UklonAPIBase, validate
from ..types.account import Auth
from ..types.address import Address
from ..types.me import Me


class UklonAPIv1(UklonAPIBase):
    _base_url = f"{UklonAPIBase._base_url}/v1"

    def account_auth(self, username: str, password: str):
        data = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        self.auth = Auth.model_validate_json(self._post("account/auth", data).text)

    @validate
    def favorite_addresses(self) -> list[Address]:
        pass

    @validate
    def me(self) -> Me:
        pass
