import pandas as pd
from .order import Order


class OrderBook:
    def __init__(self, current_time):
        self.bid_list = []  # 买盘列表
        self.ask_list = []  # 卖盘列表
        self.latest_time = current_time
        self.PRE_AUCTION_TIME = current_time.replace(hour=9, minute=15, second=0)
        self.OPEN_TIME = current_time.replace(hour=9, minute=30, second=0)
        self.AFTER_AUCTION_TIME = current_time.replace(hour=14, minute=57, second=0)

    def submit_order(self, uid, is_delete, is_buy, quantity, price, time_submitted, is_ours=False):
        if is_delete:
            if is_buy:
                self.bid_list = [i for i in self.bid_list if i.uid != uid]
            else:
                self.ask_list = [i for i in self.ask_list if i.uid != uid]
        else:
            if is_buy:
                self.bid_list.append(Order(uid=uid, is_buy=is_buy, quantity=quantity, price=price,
                                           timestamp=time_submitted, is_ours=is_ours))
            else:
                self.ask_list.append(Order(uid=uid, is_buy=is_buy, quantity=quantity, price=price,
                                           timestamp=time_submitted, is_ours=is_ours))
            self.sort()
            self.latest_time = max(time_submitted, self.latest_time)
            self.matching()

    # TODO
    def matching(self):  # 撮合
        if self.latest_time <= self.OPEN_TIME:  # 盘前集合竞价
            if self.latest_time == self.OPEN_TIME:  # 盘前集中成交
                pass
        elif self.latest_time <= self.AFTER_AUCTION_TIME:  # 盘中连续竞价
            pass
        else:  # 盘后集合竞价
            pass

    def sort(self):
        self.bid_list.sort(key=lambda x: (-x.price, x.timestamp))
        self.ask_list.sort(key=lambda x: (x.price, x.timestamp))

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
    def _bid_prices(self):
        return sorted(list(set([i.price for i in self.bid_list])), reverse=True)

    @property
    def _ask_prices(self):
        return sorted(list(set([i.price for i in self.ask_list])))

    @property
    def _bid_vol(self):
        return [sum([i.quantity for i in self.bid_list if i.price == p]) for p in self._bid_prices]

    @property
    def _ask_vol(self):
        return [sum([i.quantity for i in self.ask_list if i.price == p]) for p in self._ask_prices]

    def __str__(self):
        return (str(self.latest_time) + "\n" + str(pd.DataFrame({'bid_v': self.bid_vol_10,
                                                                 'bid_p': self.bid_prices_10,
                                                                 'ask_p': self.ask_prices_10,
                                                                 'ask_v': self.ask_vol_10})))
