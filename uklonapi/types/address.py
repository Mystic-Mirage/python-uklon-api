from pydantic import BaseModel


class Point(BaseModel):
    lat: float
    lng: float


class AddressPoint(BaseModel):
    address_name: str
    house_number: str
    source_type: str
    point: Point


class Address(BaseModel):
    id: str
    name: str
    city_id: int
    created_at: str
    type: str
    comment: str
    address_point: AddressPoint
