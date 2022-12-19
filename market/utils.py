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

def find_idx_gt(search_list, search_number):
    return next(idx for idx, vol in enumerate(search_list) if vol > search_number)
