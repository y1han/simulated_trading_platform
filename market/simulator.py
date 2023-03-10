from datetime import datetime, timedelta
import pandas as pd
from .orderbook import OrderBook
from .orderflow_handling import *


class Simulator:
    def __init__(self, code, file_path="./data/", date=None):
        self.order_flow = combined_order_transaction(code, file_path, date)
        self.submitted_order_flow = []
        self.date = datetime.strptime(str(self.order_flow["MDDate"][0]), '%Y%m%d')
        self.current_time = self.date + timedelta(hours=9, minutes=15, seconds=0)
        self.order_flow["MDTime"] = self.transform_time(self.date, self.order_flow["MDTime"])
        self.current_batch_orders = pd.DataFrame([])
        self.order_book = OrderBook(self.current_time)
        self._break_time = [self.date + timedelta(hours=11, minutes=30, seconds=0),
                            self.date + timedelta(hours=13, minutes=0, seconds=0)]

    def next_step(self, strategy_orders=None, update_interval=timedelta(seconds=3)):
        self.order_book.period_refresh()
        self.fetch_batch_orders(update_interval)
        self.order_book.latest_time = self.current_time
        self.insert_strategy_orders(strategy_orders)
        self.insert_historical_orders()
        self.order_book.auction_matching()
        self.order_book.update_record(update_interval)
        self.update_time(update_interval)
        return self.current_time - update_interval

    def update_time(self, update_interval):
        if self._break_time[0] <= self.current_time < self._break_time[1]:
            self.current_time = self._break_time[1]
        else:
            if self.current_time.minute in [0, 30] and self.current_time.second == 0:
                print(self.current_time)
            self.current_time += update_interval

    def fetch_batch_orders(self, update_interval):
        self.current_batch_orders = self.order_flow[
            (self.order_flow["MDTime"] <= self.current_time) &
            (self.order_flow["MDTime"] > self.current_time - update_interval)]

    def insert_strategy_orders(self, strategy_orders):
        if strategy_orders is not None:
            for is_delete, order in strategy_orders:
                if is_delete:
                    self.order_book.submit_order(uid=order.uid,
                                                 is_delete=is_delete,
                                                 is_buy=order.is_buy,
                                                 time_submitted=self.current_time)
                else:
                    self.order_book.submit_order(uid=order.uid,
                                                 is_delete=is_delete,
                                                 is_buy=order.is_buy,
                                                 time_submitted=self.current_time,
                                                 quantity=order.quantity,
                                                 price=order.price,
                                                 is_ours=True)

    def insert_historical_orders(self):
        for _, orders in self.current_batch_orders.iterrows():
            self.order_book.submit_order(uid=orders["OrderNO"],
                                         is_delete=(orders["OrderType"] == 10),
                                         is_buy=(orders["OrderBSFlag"] == 1),
                                         quantity=orders["OrderQty"],
                                         price=orders["OrderPrice"],
                                         time_submitted=orders["MDTime"])

    @staticmethod
    def transform_time(date, time_series):
        time_series = time_series.astype(str)
        return pd.offsets.DateOffset(years=date.year-1900, months=date.month-1, days=date.day-1) + pd.to_datetime(
            time_series, format="%H%M%S%f")

    def reset(self):
        del self.order_book
        self.submitted_order_flow = []
        self.date = datetime.strptime(str(self.order_flow["MDDate"][0]), '%Y%m%d')
        self.current_time = self.date + timedelta(hours=9, minutes=15, seconds=0)
        self.current_batch_orders = pd.DataFrame([])
        self.order_book = OrderBook(self.current_time)
