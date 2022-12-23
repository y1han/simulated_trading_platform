import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market import OrderBook
from visualization.config import *


def draw_price_series(orderbook: OrderBook):
    orderbook.historical_orderbook.set_index("time")["close"].between_time(OPEN_TIME, CLOSE_TIME).plot()
    plt.show()
