import numpy as np
import pandas as pd
from .order import Order
from .utils import *


class OrderBook:
    def __init__(self, current_time):
        self.bid_list = []  # 买盘列表
        self.ask_list = []  # 卖盘列表
        self.historical_order = []  # 历史订单列表
        self.historical_transaction = pd.DataFrame([],
                                                   columns=["time", "price", "vol", "bid_uid", "ask_uid",
                                                            "is_ours", "our_direction", "BSFlag"])  # 成交序列
        self.historical_orderbook = pd.DataFrame([],
                                                 columns=["time"] +
                                                         ["open", "close", "high", "low"] +
                                                         ["bid_p_" + str(i) for i in range(1, 11)] +
                                                         ["bid_v_" + str(i) for i in range(1, 11)] +
                                                         ["ask_p_" + str(i) for i in range(1, 11)] +
                                                         ["ask_v_" + str(i) for i in range(1, 11)] +
                                                         ["buy_volume", "sell_volume"]
                                                 )
        self.latest_time = current_time
        self.period_prices = []
        self._PRE_AUCTION_TIME = current_time.replace(hour=9, minute=15, second=0)
        self._PRE_AUCTION_MATCH_TIME = current_time.replace(hour=9, minute=25, second=0)
        self._OPEN_TIME = current_time.replace(hour=9, minute=30, second=0)
        self._AFTER_AUCTION_TIME = current_time.replace(hour=14, minute=57, second=0)
        self._AFTER_AUCTION_MATCH_TIME = current_time.replace(hour=15, minute=00, second=0)

    def submit_order(self, uid, is_delete, is_buy, time_submitted, quantity=0, price=0, is_ours=False):
        if is_delete:
            if self.get_historical_order(uid) is None:
                existing_order = self.get_order(uid, is_buy)
                self.remove_order(uid=uid, is_buy=is_buy)
                self.historical_order.append(existing_order)
        elif quantity > 0:
            if is_buy:
                self.bid_list.append(Order(uid=uid, is_buy=is_buy, quantity=quantity, price=price,
                                           time_submitted=time_submitted, is_ours=is_ours))
            else:
                self.ask_list.append(Order(uid=uid, is_buy=is_buy, quantity=quantity, price=price,
                                           time_submitted=time_submitted, is_ours=is_ours))
            self.sort()
            self.trade_matching(time_submitted)

    def auction_matching(self):  # 集合竞价撮合
        if self.latest_time <= self._OPEN_TIME:  # 盘前集合竞价
            if self.latest_time == self._PRE_AUCTION_MATCH_TIME:  # 盘前集中成交
                self._auction_process()
        elif self._AFTER_AUCTION_TIME <= self.latest_time <= self._AFTER_AUCTION_MATCH_TIME:  # 盘后集合竞价
            if self.latest_time == self._AFTER_AUCTION_MATCH_TIME:  # 盘后集中成交
                self._auction_process()

    def trade_matching(self, time_submitted):  # 连续竞价撮合
        if self._OPEN_TIME <= self.latest_time < self._AFTER_AUCTION_TIME:
            while self.best_bid >= self.best_ask:
                bid = self.bid_list[0]
                ask = self.ask_list[0]

                vol = min(bid.remaining_quantity, ask.remaining_quantity)

                is_ours, our_direction = check_our_orders(ask, bid)
                trade_price = ask.price if bid.time_submitted > ask.time_submitted else bid.price
                bs_flag = 1 if bid.time_submitted > ask.time_submitted else -1

                bid.strike_price = update_strike_price(bid, trade_price, vol)
                ask.strike_price = update_strike_price(ask, trade_price, vol)
                self.historical_transaction.loc[len(self.historical_transaction)] = [time_submitted, trade_price,
                                                                                     vol, bid.uid,
                                                                                     ask.uid, is_ours,
                                                                                     our_direction, bs_flag]
                self.period_prices.append(trade_price)
                bid.matched_quantity += vol
                ask.matched_quantity += vol
                self._postprocess_order(bid, time_submitted)
                self._postprocess_order(ask, time_submitted)

    def _auction_process(self):
        auction_price, auction_vol = auction_price_match(bid_p=self._bid_prices, ask_p=self._ask_prices,
                                                         bid_vol=self._bid_vol, ask_vol=self._ask_vol)
        self.auction_order_match(remaining_vol=auction_vol, auction_price=auction_price)

    # 集合竞价订单提交
    def auction_order_match(self, remaining_vol, auction_price):
        for bid in self.bid_list:
            if bid.price >= auction_price:
                while bid.remaining_quantity != 0:
                    ask = self.ask_list[0]
                    vol = min(bid.remaining_quantity, ask.remaining_quantity)

                    is_ours, our_direction = check_our_orders(ask, bid)
                    if remaining_vol == 0:
                        break
                    else:
                        matched_vol = min(vol, remaining_vol)
                        bid.strike_price = update_strike_price(bid, auction_price, matched_vol)
                        ask.strike_price = update_strike_price(ask, auction_price, matched_vol)
                        bid.matched_quantity += matched_vol
                        ask.matched_quantity += matched_vol
                        self.period_prices.append(auction_price)
                        self.historical_transaction.loc[len(self.historical_transaction)] = [self.latest_time,
                                                                                             auction_price, matched_vol,
                                                                                             bid.uid, ask.uid,
                                                                                             is_ours, our_direction, 0]
                        remaining_vol -= matched_vol

                    self._postprocess_order(ask, self.latest_time)
            self._postprocess_order(bid, self.latest_time)

    def period_prices_refresh(self):
        self.period_prices = [self.period_prices[-1]] if len(self.period_prices) > 0 else []

    def _postprocess_order(self, order, time_submitted):
        if order.remaining_quantity == 0:
            order.time_finished = time_submitted
            self.remove_order(order.uid, order.is_buy)
            self.historical_order.append(order)
        self.sort()

    def sort(self):
        self.bid_list.sort(key=lambda x: (-x.price, x.time_submitted))
        self.ask_list.sort(key=lambda x: (x.price, x.time_submitted))

    @property
    def best_ask(self):
        return self.ask_list[0].price if len(self.ask_list) > 0 else 0

    @property
    def best_bid(self):
        return self.bid_list[0].price if len(self.bid_list) > 0 else 0

    @property
    def bid_ask_spread(self):
        return (self.best_ask - self.best_bid) / self.best_bid

    @property
    def mid_price(self):
        return (self.best_ask + self.best_bid) / 2

    @property
    def bid_prices_10(self):
        return self._bid_prices[:10]

    @property
    def ask_prices_10(self):
        return self._ask_prices[:10]

    @property
    def bid_vol_10(self):
        return self._bid_vol[:10]

    @property
    def ask_vol_10(self):
        return self._ask_vol[:10]

    @property
    def total_bid_vol(self):
        return sum(self._bid_vol)

    @property
    def total_ask_vol(self):
        return sum(self._ask_vol)

    @property
    def bid_cum_vol_10(self):
        return list(np.cumsum(self._bid_vol[:10]))

    @property
    def ask_cum_vol_10(self):
        return list(np.cumsum(self._ask_vol[:10]))

    @property
    def our_historical_orders(self):
        return [order for order in self.historical_order if order.is_ours]

    @property
    def our_deals(self):
        return self.historical_transaction[self.historical_transaction["is_ours"]]

    @property
    def our_net_holdings(self):
        return sum(self.our_deals.get("vol", [0]) * self.our_deals.get("our_direction", 0))

    @property
    def our_gross_cost(self):
        return -sum(self.our_deals.get("vol", [0]) * self.our_deals.get("price", 0) *
                    self.our_deals.get("our_direction", 0))

    @property
    def our_avg_cost(self):
        bid_ls = self.our_deals[self.our_deals["our_direction"] == 1]
        ask_ls = self.our_deals[self.our_deals["our_direction"] == -1]
        return (
            sum(bid_ls.get("vol", [0]) * bid_ls.get("price", 0)) / sum(bid_ls.get("vol", [1])),
            sum(ask_ls.get("vol", [0]) * ask_ls.get("price", 0)) / sum(ask_ls.get("vol", [1]))
        )

    @property
    def our_active_orders(self):
        return [(i.uid, True) for i in self.bid_list if i.is_ours] + \
               [(i.uid, False) for i in self.ask_list if i.is_ours]

    @property
    def _bid_prices(self):
        return sorted(list(set([i.price for i in self.bid_list])), reverse=True)

    @property
    def _ask_prices(self):
        return sorted(list(set([i.price for i in self.ask_list])))

    @property
    def _bid_vol(self):
        return [sum([i.remaining_quantity for i in self.bid_list if i.price == p]) for p in self._bid_prices]

    @property
    def _ask_vol(self):
        return [sum([i.remaining_quantity for i in self.ask_list if i.price == p]) for p in self._ask_prices]

    def update_record(self, update_interval):
        record = [np.nan] * 47
        record[0] = self.latest_time
        if len(self.period_prices) > 0:
            record[1] = self.period_prices[0]
            record[2] = self.period_prices[-1]
            record[3] = max(self.period_prices)
            record[4] = min(self.period_prices)
        record[5: 5 + len(self.bid_prices_10)] = self.bid_prices_10
        record[15: 15 + len(self.bid_cum_vol_10)] = self.bid_cum_vol_10
        record[25: 25 + len(self.ask_prices_10)] = self.ask_prices_10
        record[35: 35 + len(self.bid_cum_vol_10)] = self.bid_cum_vol_10
        record[-2] = sum(self._period_transactions(update_interval, bs_flag=1)["vol"])
        record[-1] = sum(self._period_transactions(update_interval, bs_flag=-1)["vol"])
        self.historical_orderbook.loc[len(self.historical_orderbook)] = record

    def _period_transactions(self, update_interval, bs_flag):
        res = self.historical_transaction.set_index("time")
        if not res.empty:
            return res[res["BSFlag"] == bs_flag].between_time((self.latest_time - update_interval).time(),
                                                              self.latest_time.time())
        else:
            return res

    def get_order(self, uid, is_buy):
        if is_buy:
            return [i for i in self.bid_list if i.uid == uid][0]
        else:
            return [i for i in self.ask_list if i.uid == uid][0]

    def get_historical_order(self, uid):
        res = [i for i in self.historical_order if i.uid == uid]
        if len(res) == 0:
            return None
        else:
            return res[0]

    def remove_order(self, uid, is_buy):
        if is_buy:
            self.bid_list = [i for i in self.bid_list if i.uid != uid]
        else:
            self.ask_list = [i for i in self.ask_list if i.uid != uid]

    def __str__(self):
        return (str(self.latest_time) + "\n" + str(pd.DataFrame({'bid_v': self.bid_vol_10,
                                                                 'bid_p': self.bid_prices_10,
                                                                 'ask_p': self.ask_prices_10,
                                                                 'ask_v': self.ask_vol_10})))
