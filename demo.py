import os
from pprint import pprint

from uklonapi import RideCondition, UklonAPI

if __name__ == "__main__":
    app_uid = os.environ["UKLON_APP_UID"]
    client_id = os.environ["UKLON_CLIENT_ID"]
    client_secret = os.environ["UKLON_CLIENT_SECRET"]
    username = os.environ["UKLON_USERNAME"]
    password = os.environ["UKLON_PASSWORD"]

    uklon = UklonAPI(app_uid, client_id, client_secret)

    auth_success = None  # `None` for auth data are loaded and valid
    if uklon.auth_load():
        if uklon.auth_expired():  # try to refresh auth data if expired
            auth_success = uklon.account_auth_refresh_token()
    else:
        auth_success = False  # fail to load auth data from a file

    if auth_success is False:  # loading / refreshing was not success
        auth_success = uklon.account_auth_password(username, password)

    if auth_success:  # `True` if auth data have been updated
        uklon.auth_save()

    me = uklon.me(update_city=True)  # or just `me = uklon.update_city()`

    cities = uklon.cities()
    city = cities.get(uklon.city_id or me.city_id)
    city_settings = uklon.city_settings()

    orders_history = uklon.orders_history(include_statistic=True)

    favorite_addresses = uklon.favorite_addresses()
    payment_methods = uklon.payment_methods()
    ride_conditions = city_settings.ride_conditions({RideCondition.NON_SMOKER})
    fare_estimate = uklon.fare_estimate(
        [favorite_addresses.home, favorite_addresses.work],
        payment_methods.default_payment_method,
        ride_conditions=ride_conditions,
        include_route_info=True,
    )
    standard = fare_estimate.standard

    pprint(me)
    pprint(city)

    pprint(orders_history)

    pprint(favorite_addresses)
    pprint(payment_methods)
    pprint(ride_conditions)
    pprint(fare_estimate)
    pprint(fare_estimate.standard)
