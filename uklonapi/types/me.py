from datetime import date, datetime

from pydantic import BaseModel


class Wallet(BaseModel):
    id: str
    currency: str
    currency_symbol: str
    amount: float


class Preferences(BaseModel):
    autosend_ride_report: bool
    show_advertisement: bool
    show_discounts: bool
    show_news: bool
    show_partners_offers: bool
    show_loyalty: bool
    updated_at: int


class Details(BaseModel):
    has_car: bool
    has_car_updated_at: datetime
    has_animal: bool
    has_animal_updated_at: datetime
    has_children: bool
    has_children_updated_at: datetime


class Me(BaseModel):
    uid: str
    phone: str
    approved_phone: bool
    email: str
    first_name: str
    rating: float
    birth_date: date
    gender: str
    city_id: int
    locale_id: int
    avatar: str
    is_corporate: bool
    is_beta: bool
    wallets: list[Wallet]
    documents: list
    preferences: Preferences
    details: Details
