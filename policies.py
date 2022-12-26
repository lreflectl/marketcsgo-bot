

def price_update_policy(
        current_price: int, lowest_market_price: int,
        min_price: int, target_price: int, position: int) -> int:
    """ Define the rules to create new price based on input values. Return new price."""

    if not (min_price < lowest_market_price <= target_price):
        return current_price

    if position > 1:
        return lowest_market_price - 1

    return current_price

