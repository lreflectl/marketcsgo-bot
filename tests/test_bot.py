import unittest
from bot import MarketBot
from data_structures import ItemOnSale


class TestMarketBot(unittest.TestCase):
    def test_update_items_without_connection(self):
        bot = MarketBot()
        bot.update_items(items_from_api=[])
        self.assertEqual(bot.items, [], msg="No items - not saving")

    def test_update_items_with_data_once(self):
        bot = MarketBot()
        data_from_api = [ItemOnSale(f'item_id_{i}', 22, 500, 'USD', 'hash name') for i in range(10)]
        bot.update_items(items_from_api=data_from_api)
        self.assertEqual(len(bot.items), len(data_from_api), msg='Different items not all saved')
        self.assertEqual(bot.items[0], ItemOnSale('item_id_0', 22, 500, 'USD', 'hash name'),
                         msg='Incorrectly saved item')

    def test_update_items_with_data_multiple_same(self):
        bot = MarketBot()
        data_from_api = [ItemOnSale(f'item_id_{i}', 22, 500, 'USD', 'hash name') for i in range(10)]
        bot.update_items(items_from_api=data_from_api)
        bot.update_items(items_from_api=data_from_api)
        bot.update_items(items_from_api=data_from_api)
        self.assertEqual(len(bot.items), len(data_from_api), msg='Saving same exact items multiple times')

    def test_update_items_with_data_multiple_different(self):
        bot = MarketBot()
        data_from_api = [ItemOnSale(f'item_id_{i}', 22, 500, 'USD', 'hash name') for i in range(10)]
        bot.update_items(items_from_api=data_from_api)

        another_data_from_api = [ItemOnSale(f'item_id_{i}', 22, 500, 'USD', 'hash name') for i in range(20)]
        bot.update_items(items_from_api=another_data_from_api)

        self.assertEqual(len(bot.items), len(another_data_from_api),
                         msg='Not both old and items')
