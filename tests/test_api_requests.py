import unittest
from api_requests import get_response_with_retries
from api_requests import get_items_on_sale_and_pending_api
from api_requests import set_price_api
from api_requests import get_item_lowest_price_api
from api_requests import get_item_lowest_price_v2_api
from data_structures import ItemOnSale


class TestApi(unittest.TestCase):
    def test_get_response_with_retries(self):
        """ Works only with internet connection """
        fail_response = get_response_with_retries('', 0)
        self.assertEqual(fail_response, None)

        good_response = get_response_with_retries('https://www.google.com', 5)
        self.assertEqual(good_response.status_code, 200)

    def test_get_items_on_sale_api(self):
        response_items = get_items_on_sale_and_pending_api()
        self.assertTrue(response_items == [] or type(response_items[0]) == ItemOnSale)

    def test_set_price_api(self):
        status = set_price_api('wrong_id', 12345)
        self.assertEqual(status, False)

    def test_get_item_lowest_price_by_hash_name_api(self):
        lowest_price = get_item_lowest_price_api('Spectrum 2 Case')
        self.assertEqual(type(lowest_price), int)

    def test_get_item_lowest_price_by_hash_name_v2_api(self):
        lowest_price = get_item_lowest_price_v2_api('Spectrum 2 Case')
        self.assertEqual(type(lowest_price), int)


if __name__ == "__main__":
    unittest.main()
