import matplotlib.pyplot as plt
from datetime import time
from market import OrderBook

OPEN_TIME = time(9, 30, 0)
CLOSE_TIME = time(14, 57, 0)


def draw_spread(orderbook: OrderBook):
    plt.plot(orderbook.bid_prices_10, orderbook.bid_cum_vol_10)
    plt.plot(orderbook.ask_prices_10, orderbook.ask_cum_vol_10)
    plt.show()


def draw_historical_spread(orderbook: OrderBook, ignore_auction=True):
    bid_p = orderbook.historical_orderbook[["time", "bid_p_1"]].set_index("time")
    ask_p = orderbook.historical_orderbook[["time", "ask_p_1"]].set_index("time")
    if ignore_auction:
        bid_p = bid_p.between_time(OPEN_TIME, CLOSE_TIME)
        ask_p = ask_p.between_time(OPEN_TIME, CLOSE_TIME)
    plt.plot(bid_p)
    plt.plot(ask_p)
    plt.show()
