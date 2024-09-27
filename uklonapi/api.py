from enum import StrEnum
from functools import wraps

from pydantic import TypeAdapter
from requests import Response, Session

from .types.account import Auth
from .types.address import Address
from .types.me import Me
from .types.payment_methods import PaymentMethods


def _uklon_api_response(method: str):
    def decorator(version, json=True):
        def _(f):
            path = f.__name__.replace("_", "-")
            return_type = f.__annotations__["return"]
            type_adapter = TypeAdapter(return_type)

            @wraps(f)
            def wrapper(self, **kwargs):
                kwargs = f(self, **kwargs) or kwargs
                kw = {"json" if json else "data": kwargs} if kwargs else {}
                response = getattr(self, method)(version, path, **kw)
                return type_adapter.validate_json(response.text)

            return wrapper

        return _

    return decorator


uklon_api_get = _uklon_api_response("_get")
uklon_api_post = _uklon_api_response("_post")


class APIVersion(StrEnum):
    V1 = "v1"
    V2 = "v2"


class UklonAPI:
    _base_url = "https://m.uklon.com.ua/api"

    def __init__(self, app_uid: str, client_id: str, client_secret: str):
        self.app_uid = app_uid
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth: Auth | None = None

        self._session = Session()

    def _url(self, version, path):
        return f"{self._base_url}/{version}/{path}"

    def _get(self, version, path) -> Response:
        url = self._url(version, path)
        headers = {
            "App_uid": self.app_uid,
            "Authorization": f"{self.auth.token_type} {self.auth.access_token}",
        }
        response = self._session.get(url, headers=headers)
        return response

    def _post(self, version, path, *, data=None, json=None) -> Response:
        url = self._url(version, path)
        headers = {"App_uid": self.app_uid}
        if self.auth:
            headers["Authorization"] = (
                f"{self.auth.token_type} {self.auth.access_token}"
            )

        json = json if data else (json or {})
        response = self._session.post(url, headers=headers, data=data, json=json)
        return response

    def _account_auth(self, grant_type, **kwargs):
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **kwargs,
        }
        response = self._post(APIVersion.V1, "account/auth", data=data)
        self.auth = Auth.model_validate_json(response.text)

    def account_auth_password(self, username: str, password: str):
        self._account_auth("password", username=username, password=password)

    def account_auth_refresh_token(self):
        self._account_auth("refresh_token", refresh_token=self.auth.refresh_token)

    @uklon_api_get(APIVersion.V1)
    def favorite_addresses(self) -> list[Address]:
        pass

    @uklon_api_get(APIVersion.V1)
    def me(self) -> Me:
        pass

    @uklon_api_post(APIVersion.V2)
    def payment_methods(self) -> PaymentMethods:
        pass
