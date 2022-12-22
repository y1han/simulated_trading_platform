from dataclasses import dataclass
from typing import Optional, List, Tuple
from market import Order


@dataclass
class Portfolio:
    cash: float
    inventory: int
    avg_stock_cost: Optional[Tuple[float, float]] = (0, 0)
    financed_value: Optional[float] = 0
    historical_orders: Optional[List[Order]] = None
    active_orders: Optional[List[Tuple[int, bool]]] = None
    order_index: int = -1

    def __post_init__(self):
        self.initial_wealth = self.net_assets

    @property
    def matched_orders(self):
        return [order for order in self.historical_orders if order.matched_quantity > 0]

    @property
    def inventory_value(self):
        return sum([order.matched_quantity * order.strike_price * (order.is_buy - 0.5) * 2
                    for order in self.matched_orders])

    @property
    def net_assets(self):
        return self.cash + self.inventory_value - self.financed_value

    @property
    def profit_margin(self):
        return self.net_assets / self.initial_wealth - 1

    @property
    def leverage(self):
        return self.financed_value / self.net_assets

    @property
    def matched_quantity(self):
        return sum([order.matched_quantity for order in self.historical_orders])
