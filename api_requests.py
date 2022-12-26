import time

from requests import get
from dotenv import load_dotenv
from os import getenv
from data_structures import ItemOnSale

load_dotenv()
sleep_after_request_secs = 0.3


def get_items_on_sale_api() -> list[ItemOnSale]:
    request = f'https://market.csgo.com/api/v2/items?key={getenv("SECRET_KEY")}'
    response_json = get(request).json()
    time.sleep(sleep_after_request_secs)  # To not exceed limit of 5 requests/sec

    max_retries = 5
    while not response_json['success']:
        response_json = get(request).json()
        time.sleep(sleep_after_request_secs)
        max_retries -= 1
        if max_retries == 0:
            return []

    # If there is no items on sale
    if not response_json['items']:
        return []

    items = []
    for item in response_json['items']:
        items.append(ItemOnSale(
            item_id=item['item_id'],
            position=item['position'],
            price=int(item['price'] * 1000),  # convert price from float to int format
            currency=item['currency'],
            market_hash_name=item['market_hash_name'],
        ))
    return items


def set_price_api(item_id: str, price: int) -> bool:
    request = f'https://market.csgo.com/api/v2/set-price' \
              f'?key={getenv("SECRET_KEY")}&item_id={item_id}&price={price}&cur=USD'
    response_json = get(request).json()
    time.sleep(sleep_after_request_secs)  # To not exceed limit of 5 requests/sec

    max_retries = 5
    while not response_json['success']:
        response_json = get(request).json()
        time.sleep(sleep_after_request_secs)
        max_retries -= 1
        if max_retries == 0:
            return False
    return True


def get_item_price_by_hash_name_api(market_hash_name: str) -> int:
    """Get minimum market price by hash_name. Return price or 0 on failure"""
    request = f'https://market.csgo.com/api/v2/prices/USD.json'
    response_json = get(request).json()
    time.sleep(sleep_after_request_secs)  # To not exceed limit of 5 requests/sec

    max_retries = 5
    while not response_json['success']:
        response_json = get(request).json()
        time.sleep(sleep_after_request_secs)
        max_retries -= 1
        if max_retries == 0:
            return 0

    lowest_price = 0
    for item in response_json['items']:
        if item['market_hash_name'] == market_hash_name:
            lowest_price = int(float(item['price']) * 1000)

    return lowest_price
