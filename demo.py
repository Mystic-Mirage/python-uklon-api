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

    pprint(uklon.me())
    pprint(favorite_addresses := uklon.favorite_addresses())
    pprint(payment_methods := uklon.payment_methods())
    pprint(uklon.orders_history(include_statistic=True))
    pprint(
        fare_estimate := uklon.fare_estimate(
            [favorite_addresses.home, favorite_addresses.work],
            payment_methods.default_payment_method,
            ride_conditions={RideCondition.NON_SMOKER},
        )
    )
    pprint(fare_estimate.standard)
