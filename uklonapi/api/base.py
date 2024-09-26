from functools import wraps

import requests
from pydantic import TypeAdapter


class UklonAPIBase:
    _base_url = "https://m.uklon.com.ua/api"

    def __init__(self, api_key):
        self.api_key = api_key

    def _url(self, path):
        return f"{self._base_url}/{path}"

    def _get(self, path) -> str:
        url = self._url(path)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        return requests.get(url, headers=headers).text


def validate(f):
    path = f.__name__.replace("_", "-")
    return_type = f.__annotations__["return"]
    type_adapter = TypeAdapter(return_type)

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        data = self._get(path, *args, **kwargs)
        return type_adapter.validate_json(data)

    return wrapper
