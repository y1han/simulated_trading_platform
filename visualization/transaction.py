import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf

from market import OrderBook
from visualization.config import *


def draw_cum_transaction(orderbook: OrderBook):
    plt.plot(orderbook.historical_transaction[["time", "vol"]].set_index("time").resample("3s").sum().cumsum())
    plt.show()


def draw_cum_trading_volume(orderbook: OrderBook):
    res = orderbook.historical_orderbook[["time", "close", "buy_volume", "sell_volume"]].set_index("time").between_time(
        OPEN_TIME, CLOSE_TIME).copy()
    res["buy_sell_diff"] = res["buy_volume"] - res["sell_volume"]
    res["close"].plot()
    res["buy_sell_diff"].plot(secondary_y=True)
    plt.show()


def draw_corr_price_volume(orderbook: OrderBook, lag=1):
    res = orderbook.historical_transaction[["time", "vol", "BSFlag", "price"]].set_index("time").between_time(OPEN_TIME,
                                                                                                              CLOSE_TIME
                                                                                                              )
    adj_vol = np.sqrt(res["vol"]) * res["BSFlag"]
    lag_price_diff = (res["price"].shift(-lag) / res["price"] - 1) * 100
    plt.scatter(adj_vol, lag_price_diff)

    adj_vol = sm.add_constant(adj_vol)
    lin_fit = sm.OLS(lag_price_diff, adj_vol, missing="drop")
    model = lin_fit.fit()
    plt.plot(adj_vol, model.predict(adj_vol), "r--")

    print(f"y = {model.params.iloc[1]:.6f}x + ({model.params.iloc[0]:.6f})")
    print(f"T-value of coefficients: \n"
          f"Coeff: \t {model.tvalues.iloc[1]:.4f} \n"
          f"Inter: \t {model.tvalues.iloc[0]:.4f}")
    plt.show()


def draw_practical_corr_price_volume(orderbook: OrderBook, lag=1):
    res = orderbook.historical_orderbook[["time", "close", "buy_volume", "sell_volume"]].set_index("time").between_time(
        OPEN_TIME, CLOSE_TIME).copy()
    res["diff"] = (res["close"].shift(-lag) / res["close"] - 1) * 100
    res["adj_vol"] = np.sqrt(abs(res["buy_volume"] - res["sell_volume"])) * (
            (res["buy_volume"] > res["sell_volume"]) - 0.5) * 2
    res = res[(res["buy_volume"] != 0) | (res["sell_volume"] != 0)]
    plt.scatter(res["adj_vol"], res["diff"])

    adj_vol = sm.add_constant(res["adj_vol"])
    lin_fit = sm.OLS(res["diff"], adj_vol, missing="drop")
    model = lin_fit.fit()
    plt.plot(adj_vol, model.predict(adj_vol), "r--")

    print(f"y = {model.params.iloc[1]:.6f}x + ({model.params.iloc[0]:.6f})")
    print(f"T-value of coefficients: \n"
          f"Coeff: \t {model.tvalues.iloc[1]:.4f} \n"
          f"Inter: \t {model.tvalues.iloc[0]:.4f}")
    plt.show()


def draw_signature_plot_series(orderbook: OrderBook):
    price_series = orderbook.historical_orderbook[["time", "close"]].set_index("time")
    res = pd.DataFrame([], columns=["lag", "var"])
    for tau in range(1, 10):
        resampled_ps = price_series.resample(str(tau) + "min"
                                             ).last().ffill().between_time(OPEN_TIME, CLOSE_TIME).between_time(
            BREAK_TIME[1], BREAK_TIME[0])
        var_r = (resampled_ps.diff() / resampled_ps).var()
        acf_series = acf(resampled_ps, nlags=500)
        var = var_r * (1 + 2 * sum([(1 - u / tau) * acf_series[u] for u in range(1, min(tau, len(acf_series)))]))
        res.loc[len(res)] = [tau, var]
    res.plot.scatter(x='lag', y='var')
    plt.show()
