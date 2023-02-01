import time

from requests import get, RequestException, Response
from json.decoder import JSONDecodeError
from dotenv import load_dotenv
from os import getenv
from data_structures import ItemOnSale

API_ITEM_STATUS = {
    'ON_SALE': '1',
    'NEED_TO_TRANSFER': '2',
    'WAITING_FOR_TRANSFER': '3',
    'READY_TO_RECEIVE': '4',
}

load_dotenv()

SLEEP_AFTER_REQUEST = 0.42
SLEEP_ON_RETRY = 2


def get_response_with_retries(request, max_retries, sleep_after_request=SLEEP_AFTER_REQUEST,
                              sleep_on_retry=SLEEP_ON_RETRY) -> Response or None:
    """ Return response or None if all retries fail. """
    for attempt in range(max_retries + 1):
        try:
            response = get(request, timeout=5)
            time.sleep(sleep_after_request)  # To not exceed limit of 5 requests/sec
            return response
        except RequestException as e:
            # print('Error occurred while executing request:', e.response)
            if attempt == max_retries:  # if it was last attempt
                # print('Failed executing request.')
                return
            # print('Retrying ...')
        time.sleep(sleep_on_retry)  # Wait more if exception occurred


def safe_json(response: Response) -> dict:
    """ Always returns json. If JSONDecodeError occurs, the output contains key 'success': False """
    try:
        return response.json()
    except JSONDecodeError as e:
        return {'success': False, 'error': f'Invalid json body from server, {e.msg}.'}


def get_items_on_sale_api() -> list[ItemOnSale]:
    """ Get items that on sale right now. Return empty list on failure or items list. """
    request = f'https://market.csgo.com/api/v2/items?key={getenv("SECRET_KEY")}'
    max_retries = 2

    response = get_response_with_retries(request, max_retries)
    if response is None:
        print('Failed on getting items on sale. Max attempts exceeded.')
        return []

    response_json = safe_json(response)
    if not response_json['success']:
        print(f'Server fail on getting items on sale. Error message: {response_json["error"]}')
        return []

    # If there is no items on sale
    if not response_json['items']:
        return []

    items = []
    for item in response_json['items']:
        if item['status'] == API_ITEM_STATUS['ON_SALE']:
            items.append(ItemOnSale(
                item_id=item['item_id'],
                position=item['position'],
                price=int(item['price'] * 1000),  # convert price from float to int format
                currency=item['currency'],
                market_hash_name=item['market_hash_name'],
            ))

    return items


def set_price_api(item_id: str, price: int) -> bool:
    """ Set price on item by its item_id. Return True if set, False on fail. """
    request = f'https://market.csgo.com/api/v2/set-price' \
              f'?key={getenv("SECRET_KEY")}&item_id={item_id}&price={price}&cur=USD'
    max_retries = 2

    # The market API allows
    response = get_response_with_retries(request, max_retries)
    if response is None:
        print('Failed on setting price. Max attempts exceeded.')
        return False

    response_json = safe_json(response)
    if not response_json['success']:
        print(f'Server fail on setting price. Error message: {response_json["error"]}')
        return False

    return True


def get_item_lowest_price_api(market_hash_name: str) -> int:
    """ Deprecated, slow version. Get minimum market price by hash_name. Return price or 0 on failure. """
    request = f'https://market.csgo.com/api/v2/prices/USD.json'
    max_retries = 2

    response = get_response_with_retries(request, max_retries)
    if response is None:
        print('Failed on getting price by name. Max attempts exceeded.')
        return 0

    response_json = safe_json(response)
    if not response_json['success']:
        print('Server fail on getting price by name.')
        return 0

    lowest_price = 0
    for item in response_json['items']:
        if item['market_hash_name'] == market_hash_name:
            lowest_price = int(float(item['price']) * 1000)
            # print('lowest price from api =', lowest_price)

    return lowest_price


def get_item_lowest_price_v2_api(market_hash_name: str) -> int:
    """ Get minimum market price by hash_name. Return price or 0 on failure. """
    request = f'https://market.csgo.com/api/v2/search-item-by-hash-name-specific' \
              f'?key={getenv("SECRET_KEY")}&hash_name={market_hash_name}'
    max_retries = 2

    response = get_response_with_retries(request, max_retries)
    if response is None:
        print('Failed on getting price by name. Max attempts exceeded.')
        return 0

    response_json = safe_json(response)
    if not response_json['success']:
        print('Server fail on getting price by name.')
        return 0

    lowest_price = 0
    if response_json['data']:
        lowest_price = response_json['data'][0]['price']
        # print('lowest price from api v2 =', lowest_price)

    return lowest_price


def get_dict_of_items_lowest_prices_api(market_hash_names: list[str]) -> dict[str, int]:
    request = 'https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?' \
              f'key={getenv("SECRET_KEY")}'
    for hash_name in market_hash_names:
        request += f'&list_hash_name[]={hash_name}'

    max_retries = 2

    response = get_response_with_retries(request, max_retries)
    if response is None:
        print('Failed on getting list of prices by name. Max attempts exceeded.')
        return {}

    response_json = safe_json(response)
    if not response_json['success']:
        print('Server fail on getting list of prices by name.')
        return {}

    lowest_prices = {}
    if response_json['data']:
        prices_dict = response_json['data']
        for key, value in prices_dict.items():
            if value[0]['price'].isdigit():
                lowest_prices[key] = int(value[0]['price'])

    return lowest_prices


if __name__ == '__main__':
    start = time.perf_counter()
    name = '★ Driver Gloves | Racing Green (Field-Tested)'
    # get_item_price_api(name)
    # print(get_item_lowest_price_v2_api(name))
    print(get_dict_of_items_lowest_prices_api([
        '★ Driver Gloves | Racing Green (Field-Tested)', '★ Hand Wraps | CAUTION! (Field-Tested)'
    ]))
    print('Exec time =', time.perf_counter() - start)
