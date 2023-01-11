

def price_update_policy(
        current_price: int, lowest_market_price: int, min_price: int, target_price: int) -> int:
    """ Define the rules to create new price based on input values. Item is pretended not first in a queue.
    Return new price. """

    # skip updating the price if lowest on market is not in our range
    if not (min_price < lowest_market_price <= target_price):
        return current_price

    return lowest_market_price - 1

