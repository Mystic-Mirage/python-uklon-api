from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel

from . import Unset
from .payment_methods import PaymentMethod


class Dispatching(BaseModel):
    name: str
    phone: str


class Driver(BaseModel):
    id: str
    name: str
    phone: str
    rating: float
    marks_count: int
    disability_type: str
    image_url: str
    registered_at: datetime
    completed_orders: int
    has_processing_orders: bool


class Rider(BaseModel):
    id: str
    name: str
    phone: str


class SomeoneElse(BaseModel):
    id: str


class OtherRider(Rider):
    ride_someone_else_info: SomeoneElse


class Creator(Rider):
    ride_someone_else: bool = Unset
    ride_someone_else_id: str = Unset


class Vehicle(BaseModel):
    license_plate: str
    comfort_level: str
    brand: str
    model: str
    color: str


class Cost(BaseModel):
    extra_cost: int
    cost_multiplier: int | float
    cost_high: int
    cost_low: int
    distance: float
    cancellation_fare: float
    cost: int
    currency: str
    currency_symbol: str


class Point(BaseModel):
    address_name: str
    lat: float
    lng: float
    type: Literal["pickup", "dropoff"] | str
    rider_id: str


class Route(BaseModel):
    comment: str
    points: list[Point]
    sector_start: str
    sector_end: str


class RideCondition(BaseModel):
    name: str
    comment: str = Unset


class Idle(BaseModel):
    free_idle_period: int
    paid_idle_period: int
    time: int
    paid_time: int
    cost: int
    total_idle_seconds: int


class Traffic(BaseModel):
    region_traffic_level: int
    route_traffic_level: int
    route_time: timedelta
    traffic_jam_intervals: list


class Order(BaseModel):
    id: str
    city_id: int
    pickup_time: datetime
    created_at: datetime
    accepted_at: datetime = Unset
    status: Literal["processing", "accepted", "running"] | str
    product_type: str
    product_conditions: list
    expiry_age: int = Unset
    dispatching: Dispatching
    driver: Driver
    riders: list[Rider | OtherRider]
    created_by: Creator
    vehicle: Vehicle
    cost: Cost
    route: Route
    payment_method: PaymentMethod
    ride_conditions: list[RideCondition]
    idle: Idle
    traffic: Traffic
    is_rate_order_available: bool
