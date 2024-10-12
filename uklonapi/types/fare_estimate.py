from uuid import UUID

from pydantic import BaseModel


class Point(BaseModel):
    name: str
    lat: float
    lng: float


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


class FareEta(Fare):
    pickup_eta: int


class FareEstimate(BaseModel):
    fare_id: UUID
    product_fares: list[Fare | FareEta]
