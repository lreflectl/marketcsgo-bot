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
        return f'Item(id:{self.item_id}, {self.market_hash_name}, ' \
               f'{self.price/1000:.3f} {self.currency}, pos:{self.position}, ' \
               f'min:{self.user_min_price}, tg:{self.user_target_price})' \
               # f'upd time: {self.last_update_time:.1f})'
