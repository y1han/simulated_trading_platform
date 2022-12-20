import market as mkt
from market import Order
from datetime import time
from portfolio import Portfolio
from strategy import avallaneda_stoikov

order_index = 9999000
sim = mkt.Simulator(code=688017, date=20220704)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=11, minute=30, second=0)
current_time = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
end_time = (end_time.hour * 60 + end_time.minute) * 60 + end_time.second

prev_mid = 95
port = Portfolio(cash=10e6, inventory=0)
while current_time < end_time:
    t = current_time / end_time
    optimal_ask, optimal_bid = avallaneda_stoikov(mid_price=prev_mid,
                                                  inventory=port.inventory,
                                                  sigma=1,
                                                  t=t,
                                                  gamma=0.5,
                                                  k=0.5)
    current_time = sim.next_step([
        (False, Order(uid=order_index, is_buy=True, price=optimal_bid, quantity=100, is_ours=True)),
        (False, Order(uid=order_index + 1, is_buy=False, price=optimal_ask, quantity=100, is_ours=True))
    ])
    current_time = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
    prev_mid = sim.order_book.mid_price
    port.inventory = sim.order_book.our_net_holdings
    port.cash = port.initial_wealth - sim.order_book.our_total_cost
    port.avg_stock_cost = sim.order_book.our_total_cost / port.inventory if port.inventory != 0 else 0
    port.historical_orders = sim.order_book.our_historical_orders
    order_index += 2
print(sim.order_book)
