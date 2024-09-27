from functools import wraps

from pydantic import TypeAdapter
from requests import Response, Session

from uklonapi.types.account import Auth


class UklonAPIBase:
    _base_url = "https://m.uklon.com.ua/api"

    def __init__(self, app_uid: str, client_id: str, client_secret: str):
        self.app_uid = app_uid
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth: Auth | None = None

        self._session = Session()

    def _url(self, path):
        return f"{self._base_url}/{path}"

    def _get(self, path) -> Response:
        url = self._url(path)
        headers = {
            "App_uid": self.app_uid,
            "Authorization": f"{self.auth.token_type} {self.auth.access_token}",
        }
        response = self._session.get(url, headers=headers)
        return response

    def _post(self, path, data) -> Response:
        url = self._url(path)
        headers = {"App_uid": self.app_uid}
        if self.auth:
            headers["Authorization"] = (
                f"{self.auth.token_type} {self.auth.access_token}"
            )

        response = self._session.post(url, headers=headers, data=data)
        return response


def validate(f):
    path = f.__name__.replace("_", "-")
    return_type = f.__annotations__["return"]
    type_adapter = TypeAdapter(return_type)

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        response = self._get(path, *args, **kwargs)
        return type_adapter.validate_json(response.text)

    return wrapper
