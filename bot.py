from api_requests import get_items_on_sale_and_pending_api
from api_requests import set_price_api
from api_requests import get_dict_of_items_lowest_prices_api
from api_requests import send_telegram_message
from policies import price_update_policy
from threading import Event, Thread
from sqlite3 import connect
from pathlib import Path
import time


class MarketBot:
    def __init__(self):
        self.items = []
        self.db_path = Path(__file__).parent.resolve() / 'bot_data.db'
        self.ITEM_UPDATE_COOL_DOWN_SECONDS = 9

    def update_items(self, items_from_api):
        fresh_items_dict = {item.item_id: item for item in items_from_api}
        if not self.items:
            self.items = list(fresh_items_dict.values())
            return

        updated_items = []
        for old_item in self.items:
            new_item = fresh_items_dict.pop(old_item.item_id, None)
            # if new item exists in items list, save min, target price and update time
            # but if there is no old items in the new list, then don't save it
            if new_item is not None:
                new_item.user_min_price = old_item.user_min_price
                new_item.user_target_price = old_item.user_target_price
                new_item.last_update_time = old_item.last_update_time
                updated_items.append(new_item)
        # add items that were newly added and weren't in list
        for new_item in fresh_items_dict.values():
            updated_items.append(new_item)

        self.items = updated_items

    def set_user_price_for_item(self, item_id, min_price, target_price, lowest_price):
        if not self.items:
            print('FAIL - item list empty')
            return

        item = None
        for itm in self.items:
            if itm.item_id == item_id:
                item = itm
                break
        if item is None:
            print('FAIL - no item with given id')
            return
        if time.time() - item.last_update_time < self.ITEM_UPDATE_COOL_DOWN_SECONDS:
            print(f'PASS (cool-down) -', item)
            return

        if item.position > 1:
            new_price = price_update_policy(
                current_price=item.price,
                lowest_market_price=lowest_price,
                min_price=min_price,
                target_price=target_price,
            )
        else:
            # if item already first or not listed, then leave it with current price
            new_price = item.price

        if new_price == item.price:
            print('PASS -', item)
            return
        if new_price < min_price:
            print('Policy Error -', item)
            return
        if target_price < min_price:
            print('User input Error -', item)
            return

        is_set = set_price_api(item.item_id, new_price)
        if is_set:
            item.price = new_price
            item.last_update_time = time.time()
            print('OK -', item)
        else:
            print('FAIL -', item)

    def set_user_price_for_all_items(self):
        if not self.items:
            print('FAIL - item list empty')
            return

        lowest_prices_dict = get_dict_of_items_lowest_prices_api(self.get_hash_names())
        for item in self.items:
            if item.user_target_price == 0 or item.user_min_price == 0:
                print('PASS (not set) -', item)
                continue
            if item.market_hash_name not in lowest_prices_dict:
                print('FAIL - could not get lowest price for item')
                continue

            lowest_price = lowest_prices_dict[item.market_hash_name]
            self.set_user_price_for_item(item.item_id, item.user_min_price, item.user_target_price, lowest_price)

    def set_target_price_for_items(self):
        if not self.items:
            print('FAIL - item list empty')
            return
        for item in self.items:
            if item.user_target_price == 0 or item.user_min_price == 0:
                print('PASS (not set) -', item)
                continue
            if time.time() - item.last_update_time < self.ITEM_UPDATE_COOL_DOWN_SECONDS:
                print(
                    f'PASS (cool-down) - the item had been already updated within {self.ITEM_UPDATE_COOL_DOWN_SECONDS} secs')
                continue

            status = set_price_api(item.item_id, item.user_target_price)
            if status:
                item.price = item.user_target_price
                item.last_update_time = time.time()
                print('OK -', item)
            else:
                print('FAIL -', item)

    def initialize_db(self):
        connection = connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS ItemsOnSale('
                       'item_id INTEGER PRIMARY KEY, '
                       'market_hash_name TEXT, '
                       'min_price INTEGER, target_price INTEGER)')
        connection.close()

    def save_item_user_prices_to_db(self, item_id: str, min_price: int, target_price: int):
        connection = connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            'REPLACE INTO ItemsOnSale (item_id, min_price, target_price)'
            f'VALUES({int(item_id)}, {min_price}, {target_price})'
        )
        connection.commit()
        connection.close()

    def get_items_user_prices_from_db(self, item_ids: list[str]) -> dict[str, tuple[int, int]] or None:
        if not item_ids:
            return
        connection = connect(self.db_path)
        cursor = connection.cursor()
        query = cursor.execute(
            'SELECT item_id, min_price, target_price FROM ItemsOnSale '
            f'WHERE item_id IN ({",".join(item_ids)})'
        )
        # Create a dictionary where keys are item_ids and values are tuples of user prices
        return {str(result[0]): (result[1], result[2]) for result in query.fetchall()}

    def get_item_ids(self) -> list[str]:
        if not self.items:
            return []

        return [item.item_id for item in self.items]

    def get_hash_names(self) -> list[str]:
        if not self.items:
            return []

        return [item.market_hash_name for item in self.items]

    def update_from_db_user_prices_for_all_items(self, user_prices_dict: dict[str, tuple[int, int]]):
        if user_prices_dict is None:
            return

        for item in self.items:
            if item.item_id in user_prices_dict:
                user_prices = user_prices_dict[item.item_id]
                item.user_min_price = user_prices[0]
                item.user_target_price = user_prices[1]
        # print('updated user prices from db')


def price_update_loop(market_bot: MarketBot, stop_event: Event, finish_event: Event):
    pending_items = []
    timer = 0
    while True:
        items_from_api, new_pending_items = get_items_on_sale_and_pending_api()
        market_bot.update_items(items_from_api)

        for item in new_pending_items:
            if item not in pending_items:
                pending_items.append(item)
                send_telegram_message(f"An Item was bought from you on MarketCSGO. To receive *{item.price/1000:.3f} "
                                      f"{item.currency}* transfer _{item.market_hash_name}_ to the buyer.")

        item_ids = market_bot.get_item_ids()
        items_user_prices = market_bot.get_items_user_prices_from_db(item_ids)
        market_bot.update_from_db_user_prices_for_all_items(items_user_prices)

        market_bot.set_user_price_for_all_items()

        if timer == 100:
            market_bot.set_target_price_for_items()  # every n iterations reset prices to the target prices
            timer = 0
        timer += 1

        if stop_event.is_set():
            stop_event.clear()
            finish_event.set()
            print('Stopping price update loop...')
            break

        # sleep(1)  # Seconds to sleep on each loop iteration


def main():
    bot = MarketBot()
    stop_event = Event()
    finish_event = Event()
    worker_thread = Thread(target=price_update_loop, args=(bot, stop_event, finish_event))
    worker_thread.start()

    user_input = input('Press Enter to stop price update loop:\n')
    if user_input == '':
        stop_event.set()

    # bot = MarketBot()
    # bot.save_item_user_prices_to_db('3981048614', 124, 0)
    # print(bot.get_items_user_prices_from_db(['3981048614', '39810486143']))

    # print(Path(__file__).parent.resolve())


if __name__ == '__main__':
    main()
