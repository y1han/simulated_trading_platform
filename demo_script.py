import market as mkt
from market import Order
from datetime import time
from portfolio import Portfolio, strategy_execution
from strategy import avallaneda_stoikov

order_index = -1
sim = mkt.Simulator(code=688363, date=20220704)

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
    current_time = sim.next_step(strategy_execution(port, optimal_bid, optimal_ask))
    current_time = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
    prev_mid = sim.order_book.mid_price
    port.inventory = sim.order_book.our_net_holdings
    port.cash = port.initial_wealth + sim.order_book.our_gross_cost
    port.avg_stock_cost = sim.order_book.our_avg_cost
    port.historical_orders = sim.order_book.our_historical_orders
    port.active_orders = sim.order_book.our_active_orders
    order_index -= 2
print(sim.order_book)
