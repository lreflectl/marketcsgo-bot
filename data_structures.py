from dataclasses import dataclass


@dataclass
class ItemOnSale:
    item_id: str
    position: int
    price: int
    currency: str
    market_hash_name: str
    user_min_price = 0
    user_target_price = 0
    last_update_time = 0.

    def __repr__(self):
        name = self.market_hash_name[:12] + '...' if len(self.market_hash_name) > 15 else self.market_hash_name
        return f'id:{self.item_id}, {name}, ' \
               f'{self.price/1000:.3f}, pos:{self.position}, ' \
               f'm/t:{self.user_min_price}/{self.user_target_price}' \
               # f'upd time: {self.last_update_time:.1f})'
