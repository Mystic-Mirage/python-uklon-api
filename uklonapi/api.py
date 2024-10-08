from contextlib import suppress
from enum import StrEnum, auto
from functools import wraps
from inspect import isfunction, isgeneratorfunction
from pathlib import Path
from types import FunctionType

from pydantic import TypeAdapter
from requests import Response, Session

from .types.account import Auth
from .types.address import Address
from .types.me import Me
from .types.payment_methods import PaymentMethods


class APIMethod(StrEnum):
    GET = auto()
    POST = auto()


class APIVersion(StrEnum):
    V1 = auto()
    V2 = auto()


class GrantType(StrEnum):
    PASSWORD = auto()
    REFRESH_TOKEN = auto()


def _uklon_api_wrapper(
    f: FunctionType, method: APIMethod, version: APIVersion, json: bool
):
    # Get a request path from the function name
    # `_` at the beginning is ignored, `__` is for `/` and `_` is for `-`
    path = f.__name__.lstrip("_").replace("__", "/").replace("_", "-")

    @wraps(f)
    def wrapper(self: "UklonAPI", *args, **kwargs):
        generator = (
            f(self, *args, **kwargs)
            if isgeneratorfunction(f)
            else (x(self, *args, **kwargs) for x in (f,))
        )

        # The first generator execution (or the first function call).
        # Expecting the updated kwargs for request is yielded/returned or None
        kwargs = next(generator) or kwargs

        kw = {"json" if json else "data": kwargs} if kwargs else {}
        response: Response = getattr(self, method)(version, path, **kw)

        data = response.json()
        try:
            # The second yield (or return) receives the response data
            # then the generator modifies it if needed and yields/returns it back
            data = generator.send(data) or data
        except StopIteration as e:
            data = e.value or data

        result = (
            TypeAdapter(return_type).validate_python(data)
            if (return_type := f.__annotations__.get("return"))
            else None
        )

        with suppress(StopIteration):
            # The third yield (or return) receives a Pydantic object
            # for example to store it
            generator.send(result)

        return result

    return wrapper


def uklon_api(
    method: APIMethod = APIMethod.GET,
    version: APIVersion = APIVersion.V1,
    *,
    json: bool = True,
):
    if isfunction(method):
        # Function passed as the first argument
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

    def _url(self, version: APIVersion, path: str) -> str:
        return f"{self._base_url}/{version}/{path}"

    def _headers(self) -> dict[str, str]:
        headers = {"App_uid": self.app_uid}
        if self.auth:
            headers["Authorization"] = (
                f"{self.auth.token_type} {self.auth.access_token}"
            )
        return headers

    def get(self, version, path) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        response = self._session.get(url, headers=headers)
        response.raise_for_status()
        return response

    def post(self, version, path, *, data=None, json=None) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        json = json if data else (json or {})
        response = self._session.post(url, headers=headers, data=data, json=json)
        response.raise_for_status()
        return response

    @uklon_api(APIMethod.POST, json=False)
    def account__auth(self, grant_type, **kwargs) -> Auth:
        yield {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **kwargs,
        }
        self.auth = yield

    def account_auth_password(self, username: str, password: str):
        self.auth = None
        self.account__auth(GrantType.PASSWORD, username=username, password=password)

    def account_auth_refresh_token(self):
        refresh_token, self.auth = self.auth.refresh_token, None
        self.account__auth(GrantType.REFRESH_TOKEN, refresh_token=refresh_token)

    def auth_save_to_file(self, filename: str = None):
        if self.auth:
            json = self.auth.model_dump_json()
            Path(filename or self._default_filename).write_text(json)

    def auth_load_from_file(self, filename: str = None):
        json = Path(filename or self._default_filename).read_text()
        self.auth = Auth.model_validate_json(json)

    @uklon_api
    def favorite_addresses(self) -> list[Address]: ...

    @uklon_api
    def me(self) -> Me: ...

    @uklon_api(APIMethod.POST, APIVersion.V2)
    def payment_methods(self) -> PaymentMethods: ...
