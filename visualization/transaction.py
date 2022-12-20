import matplotlib.pyplot as plt
from market import OrderBook


def draw_cum_transaction(orderbook: OrderBook):
    plt.plot(orderbook.historical_transaction[["time", "vol"]].set_index("time").resample("3s").sum().cumsum())
    plt.show()
