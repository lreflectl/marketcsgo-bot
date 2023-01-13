import unittest
from policies import price_update_policy


class TestPolicies(unittest.TestCase):
    def test_price_update_policy(self):
        new_price = price_update_policy(
            current_price=1200,
            lowest_market_price=1100,
            min_price=900,
            target_price=1300
        )
        # Check price update inside of the min-target bounds
        self.assertEqual(new_price, 1099)

        new_price = price_update_policy(
            current_price=1200,
            lowest_market_price=700,
            min_price=900,
            target_price=1300
        )
        # Check the min bound
        self.assertEqual(new_price, 1200)

        new_price = price_update_policy(
            current_price=1200,
            lowest_market_price=700,
            min_price=700,
            target_price=1300
        )
        # Check the exact min bound
        self.assertEqual(new_price, 1200)

        new_price = price_update_policy(
            current_price=1200,
            lowest_market_price=1500,
            min_price=900,
            target_price=1300
        )
        # Check the target bound
        self.assertEqual(new_price, 1300)


if __name__ == "__main__":
    unittest.main()
