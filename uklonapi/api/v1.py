from .base import UklonAPIBase, validate
from ..types.account import Auth
from ..types.address import Address
from ..types.me import Me


class UklonAPIv1(UklonAPIBase):
    _base_url = f"{UklonAPIBase._base_url}/v1"

    def _account_auth(self, grant_type, **kwargs):
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **kwargs,
        }
        self.auth = Auth.model_validate_json(self._post("account/auth", data).text)

    def account_auth_password(self, username: str, password: str):
        self._account_auth("password", username=username, password=password)

    def account_auth_refresh_token(self):
        self._account_auth("refresh_token", refresh_token=self.auth.refresh_token)

    @validate
    def favorite_addresses(self) -> list[Address]:
        pass

    @validate
    def me(self) -> Me:
        pass
