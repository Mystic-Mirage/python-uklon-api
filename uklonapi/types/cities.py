from typing import Iterator

from pydantic import BaseModel, RootModel


class Currency(BaseModel):
    code: str
    symbol: str
    precision: int


class Location(BaseModel):
    lat: float
    lng: float


class City(BaseModel):
    id: int
    code: str
    name: str
    time_zone: int
    currency: Currency
    country_code: str
    calling_code: str
    location: Location


class Cities(RootModel[list[City]]):
    def __iter__(self) -> Iterator[City]:
        return iter(self.root)

    def __repr__(self):
        return f"{self.__repr_name__()}({self.root!r})"

    def get(self, id_: int) -> City:
        return next((city for city in self.root if city.id == id_), None)
