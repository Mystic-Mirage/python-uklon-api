from datetime import datetime

from pydantic import BaseModel


class CityPreferences(BaseModel):
    city_id: int
    preselected_ride_conditions: list[str]
    updated_at: datetime


class CitySettings(BaseModel):
    city_preferences: CityPreferences
