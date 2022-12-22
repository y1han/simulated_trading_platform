import matplotlib.pyplot as plt
from datetime import time, datetime
from market import OrderBook
from visualization.config import *


def draw_spread(orderbook: OrderBook, given_time: time):
    df = orderbook.historical_orderbook.set_index("time")
    given_time = df.index[0].replace(hour=given_time.hour, minute=given_time.minute, second=given_time.second)
    spread = df.iloc[df.index.get_loc(given_time, method='nearest')]
    plt.plot(list(spread[4:14]), list(spread[14:24]))
    plt.plot(list(spread[24:34]), list(spread[34:44]))
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


def draw_order_book_depth_trend(orderbook: OrderBook, moving_unit=0.01):
    orderbook_series = orderbook.historical_orderbook.set_index("time").between_time(OPEN_TIME, CLOSE_TIME)
    orderbook_series["bid_depth"] = 0
    orderbook_series["ask_depth"] = 0
    for i in range(1, 10):
        orderbook_series["bid_depth"] += (orderbook_series["bid_p_" + str(i + 1)] - orderbook_series[
            "bid_p_" + str(i)]) / moving_unit - 1
        orderbook_series["ask_depth"] += (orderbook_series["ask_p_" + str(i + 1)] - orderbook_series[
            "ask_p_" + str(i)]) / moving_unit - 1
    orderbook_series[["bid_depth", "ask_depth"]].plot()
    orderbook_series["close"].plot(secondary_y=True, alpha=0.5, color="grey")
    plt.show()
