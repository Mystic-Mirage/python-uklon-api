import os
from pprint import pprint

from requests import HTTPError

from uklonapi import UklonAPI

if __name__ == "__main__":
    uklon = UklonAPI(
        os.environ["APP_UID"], os.environ["CLIENT_ID"], os.environ["CLIENT_SECRET"]
    )

    auth_success = False
    try:
        uklon.auth_load_from_file()
        uklon.account_auth_refresh_token()
    except (FileNotFoundError, HTTPError):
        pass
    else:
        auth_success = True

    if not auth_success:
        uklon.account_auth_password(os.environ["USERNAME"], os.environ["PASSWORD"])

    uklon.auth_save_to_file()

    pprint(uklon.me())
    pprint(uklon.favorite_addresses())
    pprint(uklon.payment_methods())
    pprint(uklon.orders_history(include_statistic=True))
