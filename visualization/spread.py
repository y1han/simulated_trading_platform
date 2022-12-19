import matplotlib.pyplot as plt
from market import OrderBook


def draw_spread(orderbook: OrderBook):
    plt.plot(orderbook.bid_prices_10, orderbook.bid_cum_vol_10)
    plt.plot(orderbook.ask_prices_10, orderbook.ask_cum_vol_10)
    plt.show()
