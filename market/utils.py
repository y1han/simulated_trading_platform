import numpy as np


# 集合竞价成交
def auction_price_match(bid_p, ask_p, bid_vol, ask_vol):
    bid_vol_cum = np.cumsum(bid_vol)
    ask_vol_cum = np.cumsum(ask_vol)

    for i, bid_price in enumerate(bid_p):
        matching_ask_vol_idx = find_idx_gt(ask_vol_cum, bid_vol_cum[i])
        matching_ask_price_idx = find_idx_gt(ask_p, bid_price)
        if matching_ask_price_idx < matching_ask_vol_idx:
            return ask_p[matching_ask_price_idx], ask_vol_cum[matching_ask_price_idx]
        else:
            if bid_price < ask_p[matching_ask_vol_idx]:
                return ask_p[matching_ask_vol_idx], bid_vol_cum[i - 1]
            elif bid_price == ask_p[matching_ask_vol_idx]:
                return bid_price, min(bid_vol_cum[i], ask_vol_cum[matching_ask_vol_idx])

    return bid_p[-1], bid_vol_cum[-1]


# 集合竞价订单提交
def auction_order_match(order_list, remaining_vol, auction_price, latest_time):
    remaining_list = []
    historical_order = []
    for order in order_list:
        if order.quantity <= remaining_vol:
            order.matched_quantity = order.quantity
            order.active = False
            order.strike_price = auction_price
            order.time_finished = latest_time
            historical_order.append(order)
            remaining_vol -= order.quantity
        elif remaining_vol == 0:
            remaining_list.append(order)
        else:
            order.matched_quantity = remaining_vol
            order.strike_price = auction_price
            remaining_list.append(order)
            historical_order.append(order)
            remaining_vol = 0
    return remaining_list, historical_order


def find_idx_gt(search_list, search_number):
    return next(idx for idx, vol in enumerate(search_list) if vol > search_number)
