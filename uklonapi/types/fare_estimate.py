from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from . import Unset


class Point(BaseModel):
    name: str
    lat: float
    lng: float


class _RideCondition(BaseModel):
    name: str
    comment: str = ""

    def __repr__(self):
        return f"RideCondition.{self.name.upper()}" + (
            f"({self.comment!r})" if self.comment else ""
        )


class RideCondition(Enum):
    BAGGAGE = _RideCondition(name="baggage")
    ANIMAL = _RideCondition(name="animal")
    CONDITIONER = _RideCondition(name="conditioner")
    ENGLISH_SPEAKER = _RideCondition(name="english_speaker")
    NON_SMOKER = _RideCondition(name="non_smoker")
    WITH_SIGN = _RideCondition(name="with_sign")
    SILENCE = _RideCondition(name="silence")

    def __call__(self, comment):
        return type(self.value)(name=self.value.name, comment=comment)

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


class Fare(BaseModel):
    availability: Availability
    initial_extra_cost: int
    product_type: str
    low: int
    high: int
    extra: int
    multiplier: float
    cancellation_fare: float
    pickup_eta: int = Unset


class FareEstimate(BaseModel):
    fare_id: UUID
    product_fares: list[Fare]
