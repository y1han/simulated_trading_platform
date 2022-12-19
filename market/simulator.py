from datetime import datetime, timedelta
import pandas as pd
import os
from .orderbook import OrderBook


class Simulator:
    def __init__(self, code, file_path="./data/", date=None):
        self.order_flow = self.read_order_flow(code, file_path, date)
        self.submitted_order_flow = []
        self.date = datetime.strptime(str(self.order_flow["MDDate"][0]), '%Y%m%d')
        self.current_time = self.date + timedelta(hours=9, minutes=15, seconds=0)
        self.order_flow["MDTime"] = self.transform_time(self.date, self.order_flow["MDTime"])
        self.current_batch_orders = pd.DataFrame([])
        self.order_book = OrderBook(self.current_time)
        self._break_time = [self.date + timedelta(hours=11, minutes=30, seconds=0),
                            self.date + timedelta(hours=13, minutes=0, seconds=0)]

    @staticmethod
    def read_order_flow(code, file_path="", date=None):
        file_path = file_path + str(code) + "/"
        order_files = [item for item in os.listdir(file_path) if "Order_0" in item]
        res = pd.read_csv(file_path + order_files[0])
        if date is None:
            date = res["MDDate"][0]
        return res[res["MDDate"] == date].reset_index(drop=True).sort_values(by=["MDDate", "MDTime"])

    def next_step(self, strategy_orders=None, update_interval=timedelta(seconds=3)):
        self.fetch_batch_orders(update_interval)
        self.order_book.latest_time = self.current_time
        self.insert_strategy_orders(strategy_orders)
        self.insert_historical_orders()
        if len(self.current_batch_orders) > 0:
            self.order_book.auction_matching()
        # print(self.order_book)
        self.update_time(update_interval)
        return (self.current_time - update_interval).time()

    def update_time(self, update_interval):
        if self._break_time[0] <= self.current_time < self._break_time[1]:
            self.current_time = self._break_time[1]
        else:
            self.current_time += update_interval

    def fetch_batch_orders(self, update_interval):
        self.current_batch_orders = self.order_flow[
            (self.order_flow["MDTime"] < self.current_time) &
            (self.order_flow["MDTime"] >= self.current_time - update_interval)]

    def insert_strategy_orders(self, strategy_orders):
        if strategy_orders is not None:
            for is_delete, order in strategy_orders:
                self.order_book.submit_order(uid=order.uid,
                                             is_delete=is_delete,
                                             is_buy=order.is_buy,
                                             quantity=order.quantity,
                                             price=order.price,
                                             time_submitted=self.current_time,
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
