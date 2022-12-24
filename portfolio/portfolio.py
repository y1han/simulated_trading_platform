from dataclasses import dataclass
from typing import Optional, List, Tuple, Set
from datetime import datetime

import numpy as np
import pandas as pd

from market import Order, OrderBook


@dataclass
class Portfolio:
    cash: float
    inventory: int
    avg_stock_cost: Optional[Tuple[float, float]] = (0, 0)
    financed_value: Optional[float] = 0
    historical_orders: Optional[List[Order]] = None
    active_orders: Optional[List[Tuple[int, bool]]] = None
    order_index: int = -1
    historical_values: Optional[pd.DataFrame] = None

    def __post_init__(self):
        self.inventory_value = self.inventory_cost
        self.initial_wealth = self.net_assets
        self.initial_cash = self.cash
        self.initial_inventory = self.inventory
        self.historical_orders = [] if self.historical_orders is None else self.historical_orders
        self.historical_values = pd.DataFrame([[np.nan, self.net_assets, self.inventory, self.cash, np.nan]],
                                              columns=["Time", "Value", "Inventory", "Cash", "Price"])

    @property
    def matched_orders(self):
        return [order for order in self.historical_orders if order.matched_quantity > 0]

    @property
    def inventory_cost(self):
        return sum([order.matched_quantity * order.strike_price * (order.is_buy - 0.5) * 2
                    for order in self.matched_orders]) if self.historical_orders is not None else 0

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

    def update_cash(self, period_order_set):
        if len(period_order_set) > 0:
            self.cash += -sum(order.trade_money * order.bs_flag for order in period_order_set)
            print(self.cash)

    def update_portfolio(self, orderbook: OrderBook, current_time: datetime):
        self.inventory += orderbook.our_period_holdings_change()
        self.historical_orders.extend(orderbook.our_period_orders)
        self.update_cash(orderbook.our_period_orders)
        self.active_orders = orderbook.our_active_orders
        self.inventory_value = self.inventory * orderbook.latest_market_price
        self.historical_values.loc[len(self.historical_values)] = [current_time, self.net_assets, self.inventory,
                                                                   self.cash, orderbook.latest_market_price]
        return self
