import matplotlib.pyplot as plt
from datetime import time, datetime
from market import OrderBook

OPEN_TIME = time(9, 30, 0)
CLOSE_TIME = time(14, 57, 0)


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
