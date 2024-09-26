from .base import UklonAPIBase, validate
from ..types.address import Address


class UklonAPIv1(UklonAPIBase):
    _base_url = f"{UklonAPIBase._base_url}/v1"

    @validate
    def favorite_addresses(self) -> list[Address]:
        pass
