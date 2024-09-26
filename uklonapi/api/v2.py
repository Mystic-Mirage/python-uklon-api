from .base import UklonAPIBase


class UklonAPIv2(UklonAPIBase):
    _base_url = f"{UklonAPIBase._base_url}/v2"
