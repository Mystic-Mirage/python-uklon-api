from pydantic import BaseModel

from .fare_estimate import Point as FarePoint


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

    def as_point(self) -> FarePoint:
        return FarePoint(
            name=", ".join(
                filter(
                    None,
                    (self.address_point.address_name, self.address_point.house_number),
                )
            ),
            lat=self.address_point.point.lat,
            lng=self.address_point.point.lng,
        )
