from datetime import datetime

from pydantic import BaseModel

from .payment_methods import PaymentMethod


class Cost(BaseModel):
    cost: int
    currency: str
    currency_symbol: str


class RoutePoint(BaseModel):
    address_name: str
    lat: float
    lng: float
    type: str
    rider_id: str


class Route(BaseModel):
    comment: str
    points: list[RoutePoint]


class Delivery(BaseModel):
    product_type: str


class Order(BaseModel):
    id: str
    pickup_time: datetime
    created_at: datetime
    status: str
    donation_amount: int
    cost: Cost
    route: Route
    payment_method: PaymentMethod
    rating: int
    order_system: str
    cancel_reason: str
    delivery: Delivery
    product_type: str
    is_receipt_available: bool
    is_rate_order_available: bool
    receipts: list


class OrdersHistory(BaseModel):
    items: list[Order]
    has_more_items: bool


class OrdersHistoryStats(OrdersHistory):
    total: int
    completed: int
    canceled: int
