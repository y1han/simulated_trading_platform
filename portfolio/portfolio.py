import math
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
        self.baseline_profit_margin = 0
        self.historical_orders = [] if self.historical_orders is None else self.historical_orders
        self.historical_values = pd.DataFrame([[np.nan, self.net_assets, self.inventory, self.cash, np.nan, np.nan]],
                                              columns=["Time", "Value", "Inventory", "Cash", "Price", "Profit (%)"])
        self.max_exposure = 0

    @property
    def matched_orders(self):
        return [order for order in self.historical_orders if order.matched_quantity > 0]

    @property
    def last_trade(self):
        return [order.time_finished for order in self.historical_orders if order.time_finished is not None][-1]

    @property
    def inventory_cost(self):
        return sum([order.matched_quantity * order.strike_price * (order.is_buy - 0.5) * 2
                    for order in self.matched_orders]) if self.historical_orders is not None else 0

    @property
    def net_assets(self):
        return self.cash + self.inventory_value - self.financed_value

    @property
    def strategy_profit_margin(self):
        return round(self.net_assets / self.initial_wealth - 1 - self.baseline_profit_margin, 6)

    @property
    def pure_transaction_profit_margin(self):
        return round((self.trade_money_sell - self.trade_money_buy) / self.trade_money_buy,
                     6) if self.trade_money_buy != 0 else 0

    @property
    def leverage(self):
        return self.financed_value / self.net_assets

    @property
    def matched_quantity(self):
        return sum([order.matched_quantity for order in self.historical_orders])

    @property
    def trade_money(self):
        return sum([order.trade_money for order in self.historical_orders])

    @property
    def trade_money_buy(self):
        return sum([order.trade_money for order in self.historical_orders if order.is_buy])

    @property
    def trade_money_sell(self):
        return sum([order.trade_money for order in self.historical_orders if not order.is_buy])

    @property
    def matched_sell_quantity(self):
        return sum([order.matched_quantity for order in self.historical_orders if not order.is_buy])

    @property
    def daily_trading_limit(self):
        return 0.95 * self.initial_inventory - self.matched_sell_quantity

    def update_cash(self, period_order_set):
        if len(period_order_set) > 0:
            self.cash += round(-sum(order.trade_money * order.bs_flag for order in period_order_set), 2)

    def transaction_cost(self, trading_cost_pct=0.001):
        return round(self.trade_money_sell * trading_cost_pct, 2)

    def update_portfolio(self, orderbook: OrderBook, current_time: datetime):
        if current_time == orderbook.PRE_AUCTION_MATCH_TIME and self.initial_wealth == self.initial_cash + self.inventory_cost:
            market_price = orderbook.mid_price if math.isnan(
                orderbook.latest_market_price) else orderbook.latest_market_price
            self.initial_wealth = self.initial_cash + self.initial_inventory * market_price
        self.baseline_profit_margin = ((self.initial_cash + self.initial_inventory * orderbook.latest_market_price
                                        ) / self.initial_wealth - 1)
        self.inventory += orderbook.our_period_holdings_change()
        self.historical_orders.extend(orderbook.our_period_orders)
        self.update_cash(orderbook.our_period_orders)
        self.active_orders = orderbook.our_active_orders
        self.inventory_value = self.inventory * orderbook.latest_market_price
        self.max_exposure = max(abs(self.inventory - self.initial_inventory), self.max_exposure)
        self.historical_values.loc[len(self.historical_values)] = [current_time, self.net_assets, self.inventory,
                                                                   self.cash, orderbook.latest_market_price,
                                                                   self.strategy_profit_margin * 100]
        # print("Time: ", current_time, "; Cash: ", self.cash, "; Inventory: ", self.inventory, "; Net Assets: ",
        #       self.net_assets, "; Profit %: ", round(self.strategy_profit_margin * 100, 2),
        #       round(self.pure_transaction_profit_margin * 100, 2))
        # print(orderbook.our_period_orders)
        return self

    def cross_day_reset(self):
        # self.daily_trading_limit = self.initial_inventory
        pass
