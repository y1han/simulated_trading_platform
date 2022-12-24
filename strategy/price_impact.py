import math

import numpy as np
from market import OrderBook, Order
from portfolio import Portfolio


def price_impact_strategy(portfolio: Portfolio, orderbook: OrderBook):
    return_orders = []
    if orderbook.is_trading:
        mid_price = orderbook.mid_price
        spread = orderbook.best_ask - mid_price
        bid_price = round(mid_price - spread + 0.01, 2)
        ask_price = round(mid_price + spread - 0.01, 2)
        quantity = min(math.floor(0.1 * portfolio.initial_inventory), 100)

        if portfolio.active_orders is not None:
            for order in portfolio.active_orders:
                return_orders.append((True, Order(uid=order[0], is_buy=order[1])))

        return_orders.extend(
            [(False, Order(uid=portfolio.order_index, is_buy=True, price=bid_price, quantity=quantity, is_ours=True)),
             (False, Order(uid=portfolio.order_index - 1, is_buy=False, price=ask_price, quantity=quantity, is_ours=True))]
        )

        portfolio.order_index -= 2
    return return_orders
