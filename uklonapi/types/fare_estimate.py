from datetime import timedelta
from enum import Enum, EnumMeta
from functools import cached_property
from uuid import UUID

from pydantic import BaseModel

from . import Unset
from .address import Address


class Point(BaseModel):
    name: str
    lat: float
    lng: float

    @classmethod
    def from_address(cls, address: Address):
        return cls(
            name=address.address_point.name,
            lat=address.address_point.point.lat,
            lng=address.address_point.point.lng,
        )


class _RideCondition(BaseModel):
    name: str
    comment: str = ""

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"RideCondition.{self.name.upper()}" + (
            f"({self.comment!r})" if self.comment else ""
        )


class RideConditionMeta(EnumMeta):
    def __call__(cls, value: object | str, *args, **kwargs):
        if isinstance(value, str):
            return cls[value.upper()]
        return super().__call__(value, *args, **kwargs)


class RideCondition(Enum, metaclass=RideConditionMeta):
    BAGGAGE = _RideCondition(name="baggage")
    ANIMAL = _RideCondition(name="animal")
    CONDITIONER = _RideCondition(name="conditioner")
    ENGLISH_SPEAKER = _RideCondition(name="english_speaker")
    NON_SMOKER = _RideCondition(name="non_smoker")
    WITH_SIGN = _RideCondition(name="with_sign")
    SILENCE = _RideCondition(name="silence")

    def __call__(self, comment):
        if comment:
            return type(self.value)(name=self.value.name, comment=comment)
        return self

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.value.name)

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    def model_dump(self, *args, **kwargs):
        return self.value.model_dump(*args, **kwargs)


class SelectedOptions(BaseModel):
    extra_cost: int
    product_type: str


class Availability(BaseModel):
    available: bool
    unavailability_reason: str = Unset


class Fare(BaseModel):
    availability: Availability
    initial_extra_cost: int
    product_type: str
    low: int
    high: int
    extra: int
    multiplier: float
    cancellation_fare: float
    pickup_eta: timedelta = Unset


class Route(BaseModel):
    distance_meters: int
    duration_seconds: timedelta


class FareEstimate(BaseModel):
    fare_id: UUID
    product_fares: list[Fare]
    route: Route = Unset

    @cached_property
    def standard(self) -> Fare | None:
        return next(
            (pf for pf in self.product_fares if pf.product_type == "Standard"), None
        )
