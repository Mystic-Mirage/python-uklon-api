from datetime import datetime

from pydantic import BaseModel

from .fare_estimate import RideCondition


class CityPreferences(BaseModel):
    city_id: int
    preselected_ride_conditions: list[str]
    updated_at: datetime


class CitySettings(BaseModel):
    city_preferences: CityPreferences

    def ride_conditions(
        self, ride_conditions: set[RideCondition] = None
    ) -> set[RideCondition]:
        return {
            *(
                RideCondition(rc)
                for rc in self.city_preferences.preselected_ride_conditions
            ),
            *(ride_conditions or ()),
        }
