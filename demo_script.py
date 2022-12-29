import market as mkt
from market import Order
from datetime import time
from portfolio import Portfolio

sim = mkt.Simulator(code=688363, date=20220704)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=15, minute=0, second=0)
port = Portfolio(cash=1e6, inventory=91000)

while current_time < end_time:
    return_orders = [
        (False,
         Order(uid=port.order_index, is_buy=True, price=sim.order_book.best_bid, quantity=100, is_ours=True)),
        (False,
         Order(uid=port.order_index, is_buy=False, price=sim.order_book.best_ask, quantity=100, is_ours=True))
    ]
    port.order_index -= 2

    if port.active_orders is not None:
        for order in port.active_orders:
            return_orders.append((True, Order(uid=order[0], is_buy=order[1])))

    current_time = sim.next_step()
    port.update_portfolio(sim.order_book, current_time)
    current_time = current_time.time()
print(sim.order_book)
