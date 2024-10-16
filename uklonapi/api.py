import time
from contextlib import suppress
from datetime import datetime
from enum import StrEnum, auto
from functools import wraps
from inspect import getfullargspec, isfunction, isgeneratorfunction, signature
from pathlib import Path
from types import FunctionType
from typing import Union, cast, get_overloads, overload
from uuid import UUID, uuid4

from pydantic import TypeAdapter
from requests import Response, Session

from .types.account import Auth
from .types.address import Address, FavoriteAddresses
from .types.cities import Cities
from .types.city_settings import CitySettings
from .types.fare_estimate import FareEstimate, Point, RideCondition, SelectedOptions
from .types.me import Me
from .types.orders import Order
from .types.orders_history import OrdersHistory, OrdersHistoryStats
from .types.payment_methods import PaymentMethod, PaymentMethods


class APIMethod(StrEnum):
    GET = auto()
    POST = auto()


class APIVersion(StrEnum):
    V1 = auto()
    V2 = auto()


class AuthGrantType(StrEnum):
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
        nonlocal path

        spec = getfullargspec(f)
        default_kwargs = {
            k: v
            for k, v in dict(
                (
                    zip(spec.args[-len(spec.defaults) :], spec.defaults)
                    if spec.defaults
                    else {}
                ),
                **(spec.kwonlydefaults or {}),
            ).items()
            if v is not None
        }
        call_kwargs = {**default_kwargs, **kwargs}

        generator = (
            f(self, *args, **call_kwargs)
            if isgeneratorfunction(f)
            else (x(self, *args, **call_kwargs) for x in (f,))
        )

        # The first generator execution (or the first function call).
        # Expecting the updated kwargs for request is yielded/returned or None
        call_kwargs = next(generator, None) or call_kwargs

        sign = signature(f)
        positionals = {k: v for k, v in zip(reversed(spec.args), reversed(args))}
        path_args = tuple(
            arg
            for param in sign.parameters.values()
            if param.kind is param.POSITIONAL_ONLY
            if (arg := positionals.get(param.name)) is not None
        )
        if path_args:
            path = (path, *path_args)

        if method == APIMethod.GET:
            kw_key = "params"
        elif json:
            kw_key = "json"
        else:
            kw_key = "data"
        kw = {kw_key: call_kwargs} if call_kwargs else {}
        response: Response = getattr(self, method)(version, path, **kw)

        return_type = f.__annotations__.get("return")
        if not return_type:
            overloads = cast(list[FunctionType], get_overloads(f))
            if overloads:
                return_type = Union[
                    *filter(
                        None, (ol.__annotations__.get("return") for ol in overloads)
                    )
                ]
        result = (
            TypeAdapter(return_type).validate_json(response.text)
            if return_type
            else None
        )

        with suppress(StopIteration):
            # A yield receives a Pydantic object to store/process it internally, for example
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


def handle_exception(exception: type[Exception] | tuple[type[Exception], ...]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except exception:
                return False
            return True

        return wrapper

    return decorator


class UklonAPI:
    _base_url = "https://m.uklon.com.ua/api"
    _default_auth_filename = "auth.json"

    def __init__(
        self, app_uid: str, client_id: str, client_secret: str, city_id: int = None
    ):
        self.app_uid = app_uid
        self.client_id = client_id
        self.client_secret = client_secret

        self.city_id = city_id

        self.auth: Auth | None = None

        self._session = Session()

    def _url(self, version: APIVersion, path: str | tuple[str, ...]) -> str:
        if isinstance(path, str):
            path = (path,)
        return "/".join((self._base_url, version, *path))

    def _headers(self) -> dict[str, str]:
        headers = {"app_uid": self.app_uid}
        if self.city_id:
            headers["city_id"] = str(self.city_id)
        if self.auth:
            headers["Authorization"] = (
                f"{self.auth.token_type} {self.auth.access_token}"
            )
        return headers

    def get(
        self, version: APIVersion, path: str | tuple[str, ...], *, params=None
    ) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        response = self._session.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def post(
        self, version: APIVersion, path: str | tuple[str, ...], *, data=None, json=None
    ) -> Response:
        url = self._url(version, path)
        headers = self._headers()
        json = json if data else (json or {})
        response = self._session.post(url, headers=headers, data=data, json=json)
        response.raise_for_status()
        return response

    @uklon_api(APIMethod.POST, json=False)
    def account__auth(self, grant_type, **kwargs) -> Auth:
        self.auth = None  # it's necessary to set the auth to None before yielding
        self.auth = yield {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **kwargs,
        }

    @handle_exception(IOError)
    def account_auth_password(self, username: str, password: str):
        self.account__auth(AuthGrantType.PASSWORD, username=username, password=password)

    @handle_exception((AttributeError, IOError))
    def account_auth_refresh_token(self):
        refresh_token = self.auth.refresh_token
        self.account__auth(AuthGrantType.REFRESH_TOKEN, refresh_token=refresh_token)

    @handle_exception(AttributeError)
    def auth_save(self, filename: str = None):
        json = self.auth.model_dump_json(indent=2) + "\n"
        Path(filename or self._default_auth_filename).write_text(json)

    @handle_exception((OSError, ValueError))
    def auth_load(self, filename: str = None):
        json = Path(filename or self._default_auth_filename).read_text()
        self.auth = Auth.model_validate_json(json)

    def auth_expired(self):
        return self.auth.access_token_exp < time.time()

    @uklon_api
    def cities(self) -> Cities: ...

    @uklon_api(version=APIVersion.V2)
    def city_settings(self) -> CitySettings: ...

    @uklon_api
    def favorite_addresses(self) -> FavoriteAddresses: ...

    @uklon_api
    def me(self, update_city=False) -> Me:
        if update_city:
            self.city_id = (yield).city_id

    def update_city(self):
        return self.me(update_city=True)

    @uklon_api(APIMethod.POST, APIVersion.V2)
    def payment_methods(self) -> PaymentMethods: ...

    @uklon_api
    def orders_history(
        self, page: int = None, page_size: int = None, *, include_statistic: bool = None
    ) -> OrdersHistory | OrdersHistoryStats: ...

    @uklon_api(APIMethod.POST)
    def fare_estimate(
        self,
        route: list[Point | Address],
        entrance: int = None,
        *,
        payment_method: PaymentMethod = None,
        ride_conditions: set[RideCondition | str] = None,
        pickup_time: datetime = None,
        include_route_info: bool = None,
        fare_id: UUID = None,
        selected_options: SelectedOptions = None,
    ) -> FareEstimate:
        data = {
            "fare_id": str(fare_id or uuid4()),
            "route": {
                "points": [
                    (
                        Point.from_address(point)
                        if isinstance(point, Address)
                        else point
                    ).model_dump()
                    for point in route
                ],
            },
        }
        if entrance:
            data["route"]["entrance"] = entrance
        if payment_method:
            data["payment_method"] = payment_method.for_fare()
        if ride_conditions:
            data["ride_conditions"] = [
                (
                    RideCondition(ride_condition)
                    if isinstance(ride_condition, str)
                    else ride_condition
                ).model_dump()
                for ride_condition in ride_conditions
            ]
        if pickup_time:
            data["pickup_time"] = int(pickup_time.timestamp())
        if include_route_info is not None:
            data["include_route_info"] = include_route_info
        if selected_options:
            data["selected_options"] = selected_options.model_dump()
        yield data

    @overload
    def orders(self) -> list[Order]: ...
    @overload
    def orders(self, order_id: str, /) -> Order: ...
    @uklon_api
    def orders(self, order_id: str = None, /): ...
