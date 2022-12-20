import matplotlib.pyplot as plt
from market import OrderBook


def draw_spread(orderbook: OrderBook):
    plt.plot(orderbook.bid_prices_10, orderbook.bid_cum_vol_10)
    plt.plot(orderbook.ask_prices_10, orderbook.ask_cum_vol_10)
    plt.show()


def draw_historical_spread(orderbook: OrderBook):
    bid_p = orderbook.historical_orderbook[["time", "bid_p_1"]].set_index("time")
    ask_p = orderbook.historical_orderbook[["time", "ask_p_1"]].set_index("time")
    plt.plot(bid_p)
    plt.plot(ask_p)
    plt.show()
