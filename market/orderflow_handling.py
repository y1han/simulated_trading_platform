import pandas as pd
import numpy as np
import os


def read_order_flow(code, file_path="", date=None):
    file_path = file_path + str(code) + "/"
    order_files = [item for item in os.listdir(file_path) if "_O" in item]
    res = pd.read_csv(file_path + order_files[0])
    if date is None:
        date = res["MDDate"][0]
    res = res[["MDDate", "MDTime", "OrderNO", "OrderType", "OrderPrice", "OrderBSFlag", "OrderQty"]]
    return res[res["MDDate"] == date].reset_index(drop=True).sort_values(by=["MDDate", "MDTime"])


def read_transaction_flow(code, file_path="", date=None):
    file_path = file_path + str(code) + "/"
    order_files = [item for item in os.listdir(file_path) if "_T" in item]
    res = pd.read_csv(file_path + order_files[0])
    if date is None:
        date = res["MDDate"][0]
    res = res[["MDDate", "MDTime", "TradeBuyNo", "TradeSellNo", "TradeBSFlag", "TradePrice", "TradeQty"]]
    return res[res["MDDate"] == date].reset_index(drop=True).sort_values(by=["MDDate", "MDTime"])


def combined_order_transaction(code, file_path="", date=None):
    order_flow = read_order_flow(code, file_path, date)
    order_flow_list = list(set(order_flow["OrderNO"]))
    transaction_flow = read_transaction_flow(code, file_path, date)
    transaction_flow["bid_need_append"] = ~transaction_flow["TradeBuyNo"].isin(order_flow_list)
    transaction_flow["ask_need_append"] = ~transaction_flow["TradeSellNo"].isin(order_flow_list)
    check_bid = transaction_flow[["TradeBuyNo", "TradeQty"]].groupby("TradeBuyNo").sum()
    check_ask = transaction_flow[["TradeSellNo", "TradeQty"]].groupby("TradeSellNo").sum()
    for i, order in order_flow.iterrows():
        if order["OrderType"] == 2:
            tmp = []
            if order["OrderBSFlag"] == 1:
                tmp = check_bid[check_bid.index == order["OrderNO"]]
            elif order["OrderBSFlag"] == 2:
                tmp = check_ask[check_ask.index == order["OrderNO"]]
            order_flow.loc[i, "OrderQty"] = max(tmp["TradeQty"].values[0] if len(tmp) > 0 else 0, order["OrderQty"])

    appended_data_bid = transaction_flow[transaction_flow["bid_need_append"]].groupby("TradeBuyNo").agg(
        {"MDDate": 'first', "MDTime": 'first', "TradeQty": np.sum, "TradePrice": np.max}).reset_index()
    appended_data_bid.columns = ["OrderNO", "MDDate", "MDTime", "OrderQty", "OrderPrice"]
    appended_data_bid["OrderType"] = 2
    appended_data_bid["OrderBSFlag"] = 1
    appended_data_bid = appended_data_bid[
        ["MDDate", "MDTime", "OrderNO", "OrderType", "OrderPrice", "OrderBSFlag", "OrderQty"]]

    appended_data_ask = transaction_flow[transaction_flow["ask_need_append"]].groupby("TradeSellNo").agg(
        {"MDDate": 'first', "MDTime": 'first', "TradeQty": np.sum, "TradePrice": np.min}).reset_index()
    appended_data_ask.columns = ["OrderNO", "MDDate", "MDTime", "OrderQty", "OrderPrice"]
    appended_data_ask["OrderType"] = 2
    appended_data_ask["OrderBSFlag"] = 2
    appended_data_ask = appended_data_ask[
        ["MDDate", "MDTime", "OrderNO", "OrderType", "OrderPrice", "OrderBSFlag", "OrderQty"]]

    order_flow = pd.concat([order_flow, appended_data_bid, appended_data_ask])
    order_flow = order_flow.sort_values(by=["MDDate", "MDTime", "OrderNO"]).reset_index(drop=True)
    delta = order_flow.groupby(order_flow["MDTime"]).cumcount()
    order_flow["MDTime"] += delta
    return order_flow
