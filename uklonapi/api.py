from enum import StrEnum
from functools import wraps
from inspect import isgenerator, isgeneratorfunction, ismethod
from pathlib import Path
from types import MethodType

from pydantic import TypeAdapter
from requests import Response, Session

from .types.account import Auth
from .types.address import Address
from .types.me import Me
from .types.payment_methods import PaymentMethods


class APIMethod(StrEnum):
    GET = "_get"
    POST = "_post"


class APIVersion(StrEnum):
    V1 = "v1"
    V2 = "v2"


def _uklon_api_wrapper(
    f: MethodType, method: APIMethod, version: APIVersion, json: bool
):
    path = f.__name__.lstrip("_").replace("__", "/").replace("_", "-")
    return_type = f.__annotations__.get("return")
    type_adapter = TypeAdapter(return_type) if return_type else None

    @wraps(f)
    def wrapper(self: "UklonAPI", *args, **kwargs):
        gen = (
            f(self, *args, **kwargs)
            if isgeneratorfunction(f)
            else iter([f(self, **kwargs)])
        )

        kwargs = next(gen) or kwargs
        kw = {"json" if json else "data": kwargs} if kwargs else {}
        response = getattr(self, method)(version, path, **kw)

        if isgenerator(gen):
            gen.send(response)

        if type_adapter:
            return type_adapter.validate_json(response.text)

    return wrapper


def uklon_api(
    method: APIMethod = APIMethod.GET,
    version: APIVersion = APIVersion.V1,
    *,
    json: bool = True,
):
    if ismethod(method):
        f, method = method, APIMethod.GET
        return _uklon_api_wrapper(f, method, version, json)

    def decorator(f):
        return _uklon_api_wrapper(f, method, version, json)

    return decorator


class UklonAPI:
    _base_url = "https://m.uklon.com.ua/api"
    _default_filename = "auth.json"

    def __init__(self, app_uid: str, client_id: str, client_secret: str):
        self.app_uid = app_uid
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth: Auth | None = None

        self._session = Session()

    def _url(self, version, path):
        return f"{self._base_url}/{version}/{path}"

    def _headers(self):
        headers = {"App_uid": self.app_uid}
        if self.auth:
            headers["Authorization"] = (
                f"{self.auth.token_type} {self.auth.access_token}"
            )
        return headers

    def _get(self, version, path) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        response = self._session.get(url, headers=headers)
        response.raise_for_status()
        return response

    def _post(self, version, path, *, data=None, json=None) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        json = json if data else (json or {})
        response = self._session.post(url, headers=headers, data=data, json=json)
        response.raise_for_status()
        return response

    @uklon_api(APIMethod.POST, json=False)
    def _account__auth(self, grant_type, **kwargs):
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **kwargs,
        }

        response = yield data

        self.auth = Auth.model_validate_json(response.text)

    def account_auth_password(self, username: str, password: str):
        self._account__auth("password", username=username, password=password)

    def account_auth_refresh_token(self):
        self._account__auth("refresh_token", refresh_token=self.auth.refresh_token)

    def account_auth_save_to_file(self, filename: str = None):
        if self.auth:
            json = self.auth.model_dump_json()
            Path(filename or self._default_filename).write_text(json)

    def account_auth_load_from_file(self, filename: str = None):
        json = Path(filename or self._default_filename).read_text()
        self.auth = Auth.model_validate_json(json)

    @uklon_api
    def favorite_addresses(self) -> list[Address]:
        pass

    @uklon_api
    def me(self) -> Me:
        pass

    @uklon_api(APIMethod.POST, APIVersion.V2)
    def payment_methods(self) -> PaymentMethods:
        pass
