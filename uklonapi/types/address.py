from enum import StrEnum, auto
from functools import cached_property
from typing import Iterator

from pydantic import BaseModel, RootModel


class Point(BaseModel):
    lat: float
    lng: float


class AddressPoint(BaseModel):
    address_name: str
    house_number: str
    source_type: str
    point: Point

    @cached_property
    def name(self):
        return ", ".join(
            filter(
                None,
                (
                    self.address_name,
                    self.house_number,
                ),
            )
        )


class Address(BaseModel):
    id: str
    name: str
    city_id: int
    created_at: str
    type: str
    comment: str
    address_point: AddressPoint


class AddressType(StrEnum):
    HOME = auto()
    WORK = auto()


class FavoriteAddresses(RootModel[list[Address]]):
    def __getitem__(self, item) -> Address:
        return self.root[item]

    def __iter__(self) -> Iterator[Address]:
        return iter(self.root)

    def __repr__(self):
        return f"{self.__repr_name__()}(home={self.home!r}, work={self.work!r}, other={self.other!r})"

    @cached_property
    def home(self) -> Address | None:
        return next(
            (address for address in self.root if address.type == AddressType.HOME), None
        )

    @cached_property
    def work(self) -> Address | None:
        return next(
            (address for address in self.root if address.type == AddressType.WORK), None
        )

    @cached_property
    def other(self) -> list[Address]:
        return [address for address in self.root if address.type not in AddressType]
