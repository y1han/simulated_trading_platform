import numpy as np


# 集合竞价成交
def auction_price_match(bid_p, ask_p, bid_vol, ask_vol):
    if len(bid_vol) > 1:
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
    else:
        return bid_p[-1], bid_vol[-1]


def find_idx_gt(search_list, search_number):
    return next(iter(idx for idx, vol in enumerate(search_list) if vol > search_number), len(search_list))


def update_strike_price(order, price, vol):
    return price if order.strike_price is None \
        else (order.strike_price * order.matched_quantity + order.price * vol) / (order.matched_quantity + vol)


def check_our_orders(ask, bid):
    is_ours = False
    our_direction = 0
    if ask.is_ours:
        is_ours = True
        our_direction = -1
    elif bid.is_ours:
        is_ours = True
        our_direction = 1

    return is_ours, our_direction


def extend_list(ls, length):
    if length > len(ls):
        return ls + [np.nan] * (length - len(ls))
    else:
        return ls
