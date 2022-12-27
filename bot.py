from api_requests import get_items_on_sale_api
from api_requests import set_price_api
from api_requests import get_item_price_by_hash_name_api
from policies import price_update_policy
from threading import Event, Thread
from time import sleep


class MarketBot:
    def __init__(self):
        self.items = []

    def update_items(self):
        self.items = get_items_on_sale_api()

    def update_item_price(self, item_idx_in_items, min_price, target_price):
        if not self.items:
            print('FAIL - item list empty')
            return

        item = self.items[item_idx_in_items]
        lowest_price_on_market = get_item_price_by_hash_name_api(item.market_hash_name)

        new_price = price_update_policy(
            current_price=item.price,
            lowest_market_price=lowest_price_on_market,
            position=item.position,
            min_price=min_price,
            target_price=target_price,
        )
        if new_price == item.price:
            print('PASS -', item)
            return
        if new_price < min_price:
            print('Policy Error -', item)
            return

        status = set_price_api(item.item_id, new_price)
        if status:
            item.price = new_price
            print('OK -', item)
        else:
            print('FAIL -', item)

    def update_all_item_prices_in_list(self):
        if not self.items:
            print('FAIL - item list empty')
            return
        for idx, item in enumerate(self.items):
            if item.user_target_price == 0 or item.user_min_price == 0:
                print('PASS (not set) -', item)
                continue
            self.update_item_price(idx, item.user_min_price, item.user_target_price)

    def set_target_prices_for_items(self):
        if not self.items:
            print('FAIL - item list empty')
            return
        for item in self.items:
            if item.user_target_price == 0 or item.user_min_price == 0:
                print('PASS (not set) -', item)
                continue
            status = set_price_api(item.item_id, item.user_target_price)
            if status:
                item.price = item.user_target_price
                print('OK -', item)
            else:
                print('FAIL -', item)


def price_update_loop(market_bot: MarketBot, stop_event: Event, finish_event: Event):
    stop_event.clear()
    finish_event.clear()
    timer = 0
    while True:
        market_bot.update_items()
        print(market_bot.items)
        market_bot.update_all_item_prices_in_list()

        if timer == 60:
            market_bot.set_target_prices_for_items()  # every minute reset prices to the target prices
            timer = 0
        timer += 1

        if stop_event.is_set():
            print('Stopping price update loop...')
            finish_event.set()
            break

        sleep(5)  # Seconds to sleep on each loop iteration


def main():
    bot = MarketBot()
    stop_event = Event()
    worker_thread = Thread(target=price_update_loop, args=(bot, stop_event))
    worker_thread.start()

    user_input = input('Press Enter to stop price update loop:\n')
    if user_input == '':
        stop_event.set()


if __name__ == '__main__':
    main()
