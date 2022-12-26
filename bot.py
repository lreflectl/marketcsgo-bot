from api_requests import get_items_on_sale_api
from api_requests import set_price_api
from api_requests import get_item_price_by_hash_name_api
from policies import price_update_policy
from data_structures import ItemOnSale
from threading import Event, Thread
from time import sleep


class MarketBot:
    def __init__(self):
        self.items = [ItemOnSale]

    def update_items(self):
        self.items = get_items_on_sale_api()

    def update_item_price(self, index_in_items, min_price, target_price):
        if not self.items:
            print('FAIL - item list empty')
            return

        item = self.items[index_in_items]
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

    def update_all_item_prices_in_list(self, desired_prices: dict[str, tuple[int, int]]):
        if not self.items:
            print('FAIL - item list empty')
            return

        for idx in range(len(self.items)):
            item_id = self.items[idx].item_id
            self.update_item_price(idx, *desired_prices[item_id])

    def set_target_prices_for_items(self, desired_prices: dict[str, tuple[int, int]]):
        if not self.items:
            print('FAIL - item list empty')
            return

        for item in self.items:
            status = set_price_api(item.item_id, desired_prices[item.item_id][1])
            if status:
                item.price = desired_prices[item.item_id][1]
                print('OK -', item)
            else:
                print('FAIL -', item)


def price_update_loop(market_bot: MarketBot, desired_prices: dict[str, tuple[int, int]], stop_event: Event):
    timer = 0
    while True:
        market_bot.update_items()
        print(market_bot.items)
        market_bot.update_all_item_prices_in_list(desired_prices)

        if timer == 60:
            market_bot.set_target_prices_for_items(desired_prices)  # every minute reset prices to target
            timer = 0
        timer += 1

        if stop_event.is_set():
            print('Stopping price update loop...')
            break

        sleep(5)  # Seconds to sleep on each loop iteration


def main():
    bot = MarketBot()
    desired_prices = {
        '3899439064': (800, 1400),
    }
    stop_event = Event()
    worker_thread = Thread(target=price_update_loop, args=(bot, desired_prices, stop_event))
    worker_thread.start()

    user_input = input('Press Enter to stop price update loop:\n')
    if user_input == '':
        stop_event.set()


if __name__ == '__main__':
    main()
