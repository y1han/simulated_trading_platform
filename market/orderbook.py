import numpy as np
import pandas as pd
from .order import Order
from .utils import *


class OrderBook:
    def __init__(self, current_time):
        self.bid_list = []  # 买盘列表
        self.ask_list = []  # 卖盘列表
        self.historical_order = []  # 历史订单列表
        self.historical_deal = pd.DataFrame([], columns=["time", "price", "vol", "bid_uid", "ask_uid"])  # 成交序列
        self.latest_time = current_time
        self._PRE_AUCTION_TIME = current_time.replace(hour=9, minute=15, second=0)
        self._PRE_AUCTION_MATCH_TIME = current_time.replace(hour=9, minute=25, second=0)
        self._OPEN_TIME = current_time.replace(hour=9, minute=30, second=0)
        self._AFTER_AUCTION_TIME = current_time.replace(hour=14, minute=57, second=0)
        self._AFTER_AUCTION_MATCH_TIME = current_time.replace(hour=15, minute=00, second=0)

    def submit_order(self, uid, is_delete, is_buy, quantity, price, time_submitted, is_ours=False):
        if is_delete:
            self.remove_order(uid=uid, is_buy=is_buy)
        else:
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
                bid.matched_quantity += vol
                ask.matched_quantity += vol

                if bid.price == ask.price:
                    bid.strike_price = self._update_strike_price(bid, bid.price, vol)
                    ask.strike_price = self._update_strike_price(ask, bid.price, vol)
                    self.historical_deal.loc[len(self.historical_deal)] = [time_submitted, bid.price, vol, bid.uid,
                                                                           ask.uid]
                elif bid.price > ask.price:
                    if bid.time_submitted > ask.time_submitted:  # Bid比Ask晚
                        bid.strike_price = self._update_strike_price(bid, ask.price, vol)
                        ask.strike_price = self._update_strike_price(ask, ask.price, vol)
                        self.historical_deal.loc[len(self.historical_deal)] = [time_submitted, ask.price, vol, bid.uid,
                                                                               ask.uid]
                    else:
                        bid.strike_price = self._update_strike_price(bid, bid.price, vol)
                        ask.strike_price = self._update_strike_price(ask, bid.price, vol)
                        self.historical_deal.loc[len(self.historical_deal)] = [time_submitted, bid.price, vol, bid.uid,
                                                                               ask.uid]
                if bid.remaining_quantity == 0:
                    bid.time_finished = time_submitted
                    self.remove_order(bid.uid, bid.is_buy)
                    self.historical_order.append(bid)
                if ask.remaining_quantity == 0:
                    ask.time_finished = time_submitted
                    self.remove_order(ask.uid, ask.is_buy)
                    self.historical_order.append(ask)
                self.sort()

    def _auction_process(self):
        auction_price, auction_vol = auction_price_match(bid_p=self._bid_prices, ask_p=self._ask_prices,
                                                         bid_vol=self._bid_vol, ask_vol=self._ask_vol)
        self.auction_order_match(remaining_vol=auction_vol, auction_price=auction_price)
        self.sort()

    # 集合竞价订单提交
    def auction_order_match(self, remaining_vol, auction_price):
        for bid in self.bid_list:
            if bid.price >= auction_price:
                while bid.remaining_quantity != 0:
                    ask = self.ask_list[0]
                    vol = min(bid.remaining_quantity, ask.remaining_quantity)

                    if vol <= remaining_vol:
                        bid.matched_quantity += vol
                        ask.matched_quantity += vol
                        bid.strike_price = self._update_strike_price(bid, auction_price, vol)
                        ask.strike_price = self._update_strike_price(ask, auction_price, vol)
                        self.historical_deal.loc[len(self.historical_deal)] = [self.latest_time, auction_price,
                                                                               vol, bid.uid, ask.uid]
                        remaining_vol -= vol
                    elif remaining_vol == 0:
                        break
                    else:
                        bid.matched_quantity += remaining_vol
                        ask.matched_quantity += remaining_vol
                        bid.strike_price = self._update_strike_price(bid, auction_price, vol)
                        ask.strike_price = self._update_strike_price(ask, auction_price, vol)
                        self.historical_deal.loc[len(self.historical_deal)] = [self.latest_time, auction_price,
                                                                               remaining_vol, bid.uid, ask.uid]
                        remaining_vol = 0

                    if ask.remaining_quantity == 0:
                        ask.time_finished = self.latest_time
                        self.remove_order(ask.uid, ask.is_buy)
                        self.historical_order.append(ask)
                        self.sort()

            if bid.remaining_quantity == 0:
                bid.time_finished = self.latest_time
                self.remove_order(bid.uid, bid.is_buy)
                self.historical_order.append(bid)
                self.sort()

    def sort(self):
        self.bid_list.sort(key=lambda x: (-x.price, x.time_submitted))
        self.ask_list.sort(key=lambda x: (x.price, x.time_submitted))

    @property
    def best_ask(self):
        return self.ask_list[0].price

    @property
    def best_bid(self):
        return self.bid_list[0].price

    @property
    def bid_ask_spread(self):
        return (self.best_ask - self.best_bid) / self.best_bid

    @property
    def mid_price(self):
        return (self.best_ask + self.best_bid) / 2

    @property
    def bid_prices_10(self):
        return self._bid_prices[:11]

    @property
    def ask_prices_10(self):
        return self._ask_prices[:11]

    @property
    def bid_vol_10(self):
        return self._bid_vol[:11]

    @property
    def ask_vol_10(self):
        return self._ask_vol[:11]

    @property
    def our_historical_orders(self):
        return [order for order in self.historical_order if order.is_ours]

    @property
    def our_deals(self):
        return self.historical_deal.where("bid_uid")

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

    @staticmethod
    def _update_strike_price(order, price, vol):
        return price if order.strike_price is None \
            else (order.strike_price * order.matched_quantity + order.price * vol) / (order.matched_quantity + vol)

    def get_order(self, uid, is_buy):
        if is_buy:
            return [i for i in self.bid_list if i.uid == uid][0]
        else:
            return [i for i in self.ask_list if i.uid == uid][0]

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
