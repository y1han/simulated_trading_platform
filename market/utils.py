import numpy as np


# 集合竞价成交
def auction_price_match(bid_p, ask_p, bid_vol, ask_vol):
    if len(bid_vol) > 1 and bid_p[0] >= ask_p[0]:
        bid_vol_cum = np.cumsum(bid_vol)
        ask_vol_cum = np.cumsum(ask_vol)

        optimal_price_bid = bid_p[0]
        optimal_vol_bid = bid_vol_cum[0]
        optimal_non_matching_vol_bid = 10e6
        for i, bid_price in enumerate(bid_p):
            matching_idx = find_max_idx_le(ask_p, bid_price)  # 最大的小于等于该bid的price
            vol = min(bid_vol_cum[i], ask_vol_cum[matching_idx])
            if vol > optimal_vol_bid:
                optimal_price_bid = bid_price
                optimal_vol_bid = vol
                optimal_non_matching_vol_bid = max(bid_vol_cum[i], ask_vol_cum[matching_idx]) - vol

        optimal_price_ask = ask_p[0]
        optimal_vol_ask = ask_vol_cum[0]
        optimal_non_matching_vol_ask = 10e6
        for i, ask_price in enumerate(ask_p):
            matching_idx = find_min_idx_ge(bid_p, ask_price)  # 最小的大于等于该ask的price
            vol = min(ask_vol_cum[i], bid_vol_cum[matching_idx])
            if vol > optimal_vol_ask:
                optimal_price_ask = ask_price
                optimal_vol_ask = vol
                optimal_non_matching_vol_ask = max(ask_vol_cum[i], bid_vol_cum[matching_idx]) - vol

        if optimal_vol_bid < optimal_vol_ask:
            optimal_price = optimal_price_ask
        elif optimal_vol_bid > optimal_vol_ask:
            optimal_price = optimal_price_bid
        else:
            if optimal_non_matching_vol_ask < optimal_non_matching_vol_bid:
                optimal_price = optimal_price_ask
            elif optimal_non_matching_vol_ask > optimal_non_matching_vol_bid:
                optimal_price = optimal_price_bid
            else:
                optimal_price = (optimal_price_ask + optimal_price_bid) / 2
        optimal_vol = max(optimal_vol_ask, optimal_vol_bid)
        return optimal_price, optimal_vol
    else:
        return 0, 0


def find_min_idx_ge(search_list, search_number):
    res = [idx for idx, vol in enumerate(search_list) if vol >= search_number]
    return res[-1] if len(res) > 0 else 0


def find_max_idx_le(search_list, search_number):
    res = [idx for idx, vol in enumerate(search_list) if vol <= search_number]
    return res[-1] if len(res) > 0 else 0


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
