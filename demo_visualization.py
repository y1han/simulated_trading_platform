import market as mkt
from datetime import time
from visualization import *


sim = mkt.Simulator(code=688017, date=20220704)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=15, minute=00, second=0)

while current_time < end_time:
    current_time = sim.next_step()
draw_historical_spread(sim.order_book)
print(sim.order_book)
