import market as mkt
from market import Order
from datetime import datetime, timedelta
from portfolio import Portfolio
from strategy import avallaneda_stoikov

order_index = 9999000
sim = mkt.Simulator(file_path="data/688001.SH/20220812/逐笔委托.csv")

sim.reset()
time = datetime(year=2022, month=8, day=12) + timedelta(hours=9, minutes=15, seconds=0)
end_time = datetime(year=2022, month=8, day=12) + timedelta(hours=10, minutes=50, seconds=0)

prev_mid = 37.45
port = Portfolio(cash=10e6, inventory=0)
while time < end_time:
    t = int(round(time.timestamp())) / int(round(end_time.timestamp()))
    optimal_ask, optimal_bid = avallaneda_stoikov(mid_price=prev_mid,
                                                  inventory=port.inventory,
                                                  sigma=1,
                                                  t=t,
                                                  gamma=0.5,
                                                  k=0.5)
    time = sim.next_step([
        (False, Order(uid=order_index, is_buy=True, price=optimal_bid, quantity=100, is_ours=True)),
        (False, Order(uid=order_index + 1, is_buy=False, price=optimal_ask, quantity=100, is_ours=True))
    ])
    prev_mid = sim.order_book.mid_price
    port.inventory = sim.order_book.our_net_holdings
    port.cash -= sim.order_book.our_total_cost
    port.avg_stock_cost = sim.order_book.our_total_cost / port.inventory if port.inventory != 0 else 0
    port.historical_orders = sim.order_book.our_historical_orders
    order_index += 2
print(sim.order_book)
