import numpy as np


def avallaneda_stoikov(mid_price, inventory, sigma, t, gamma, k):
    """
    Inventory position (q)
    Time until the trading session ends (T-t)
    Risk factor (γ)
    Order book depth (κ)
    """
    reserve_price = mid_price - inventory * gamma * (sigma ** 2) * (1 - t)
    reserve_spread = 2 * np.log(1 + gamma / k) / gamma
    optimal_ask = reserve_price + reserve_spread
    optimal_bid = reserve_price - reserve_spread
    return optimal_ask, optimal_bid
