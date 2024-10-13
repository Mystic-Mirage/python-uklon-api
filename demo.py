import os
from pprint import pprint

from uklonapi import RideCondition, UklonAPI

if __name__ == "__main__":
    uklon = UklonAPI(
        os.environ["APP_UID"], os.environ["CLIENT_ID"], os.environ["CLIENT_SECRET"]
    )

    auth_success = uklon.auth_load_from_file() and uklon.account_auth_refresh_token()
    if not auth_success:
        uklon.account_auth_password(os.environ["USERNAME"], os.environ["PASSWORD"])
        uklon.auth_save_to_file()

    me = uklon.me()
    uklon.city_id = me.city_id

    cities = uklon.cities()
    city = cities.get(me.city_id)
    city_settings = uklon.city_settings()

    orders_history = uklon.orders_history(include_statistic=True)

    favorite_addresses = uklon.favorite_addresses()
    payment_methods = uklon.payment_methods()
    ride_conditions = {
        RideCondition.NON_SMOKER,
        *city_settings.city_preferences.preselected_ride_conditions,
    }
    fare_estimate = uklon.fare_estimate(
        [favorite_addresses.home, favorite_addresses.work],
        payment_methods.default_payment_method,
        ride_conditions=ride_conditions,
    )
    standard = fare_estimate.standard

    pprint(me)
    pprint(city)

    pprint(city_settings.city_preferences.preselected_ride_conditions)

    pprint(orders_history)

    pprint(favorite_addresses)
    pprint(payment_methods)
    pprint(fare_estimate.standard)
