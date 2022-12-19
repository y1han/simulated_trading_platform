from dataclasses import dataclass
from typing import Optional, List
from market import Order


@dataclass
class Portfolio:
    cash: float
    inventory: int
    avg_stock_cost: Optional[float] = 0
    financed_value: Optional[float] = 0
    historical_orders: Optional[List[Order]] = None

    def __post_init__(self):
        self.initial_wealth = self.net_assets

    @property
    def inventory_value(self):
        return self.inventory * self.avg_stock_cost

    @property
    def net_assets(self):
        return self.cash + self.inventory_value - self.financed_value

    @property
    def profit_margin(self):
        return self.net_assets / self.initial_wealth - 1

    @property
    def leverage(self):
        return self.financed_value / self.net_assets
